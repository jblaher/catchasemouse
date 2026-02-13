"""Pygame GUI: 20x30 grid with drawn cat, mouse, and obstacles. WASD/arrows, N=new game, Q=quit, L=leaderboard."""

import random
import sys

from catgame.game.turn import apply_move
from catgame.leaderboard import add_score, get_top10
from catgame.models import GameState, Position, ROWS, COLS
from catgame.placement.placement import create_game

try:
    import pygame
except ImportError as e:
    raise ImportError("Pygame GUI requires pygame. Install with: pip install 'catgame[gui]' or pip install pygame") from e

# Layout
CELL_SIZE = 28
GRID_WIDTH = COLS * CELL_SIZE
GRID_HEIGHT = ROWS * CELL_SIZE
STATUS_HEIGHT = 36
WINDOW_WIDTH = GRID_WIDTH
WINDOW_HEIGHT = GRID_HEIGHT + STATUS_HEIGHT

# Colors (R, G, B)
COLOR_EMPTY = (40, 44, 52)
COLOR_OBSTACLE = (120, 80, 60)
COLOR_OBSTACLE_LINE = (90, 60, 45)
COLOR_CAT = (230, 140, 60)
COLOR_CAT_FACE = (60, 40, 20)
COLOR_WHISKER = (220, 210, 200)
COLOR_MOUSE = (160, 160, 160)
COLOR_MOUSE_FACE = (80, 80, 80)
COLOR_GRID_LINE = (60, 64, 72)
COLOR_STATUS_BG = (50, 54, 62)
COLOR_STATUS_TEXT = (220, 220, 220)
COLOR_WIN = (100, 200, 100)

KEY_TO_DIR = {
    pygame.K_UP: "up",
    pygame.K_w: "up",
    pygame.K_DOWN: "down",
    pygame.K_s: "down",
    pygame.K_LEFT: "left",
    pygame.K_a: "left",
    pygame.K_RIGHT: "right",
    pygame.K_d: "right",
}


def _cell_rect(row: int, col: int) -> "pygame.Rect":
    """Rect for the inner cell (excluding grid line)."""
    return pygame.Rect(col * CELL_SIZE + 1, row * CELL_SIZE + 1, CELL_SIZE - 1, CELL_SIZE - 1)


def _draw_empty(surface: "pygame.Surface", rect: "pygame.Rect") -> None:
    pygame.draw.rect(surface, COLOR_EMPTY, rect)


def _draw_obstacle(surface: "pygame.Surface", rect: "pygame.Rect") -> None:
    pygame.draw.rect(surface, COLOR_OBSTACLE, rect)
    # Brick lines
    cx, cy = rect.centerx, rect.centery
    pygame.draw.line(surface, COLOR_OBSTACLE_LINE, (rect.left, cy), (rect.right, cy), 1)
    pygame.draw.line(surface, COLOR_OBSTACLE_LINE, (cx, rect.top), (cx, rect.bottom), 1)


def _draw_cat(surface: "pygame.Surface", rect: "pygame.Rect") -> None:
    cx, cy = rect.centerx, rect.centery
    r = min(rect.w, rect.h) // 2 - 3
    # Head
    pygame.draw.circle(surface, COLOR_CAT, (cx, cy), r)
    # Ears: pointed triangles with inner ear
    ear_h = max(5, r * 3 // 4)
    ear_w = max(4, r // 2)
    left_ear = [(cx - ear_w, cy - r - ear_h), (cx - ear_w * 2, cy - r + 1), (cx - 1, cy - r + 1)]
    pygame.draw.polygon(surface, COLOR_CAT, left_ear)
    pygame.draw.polygon(surface, COLOR_CAT_FACE, left_ear, 1)
    inner_left = [(cx - ear_w, cy - r - ear_h + 2), (cx - ear_w * 2 + 2, cy - r), (cx - 2, cy - r)]
    pygame.draw.polygon(surface, COLOR_CAT_FACE, inner_left)
    right_ear = [(cx + ear_w, cy - r - ear_h), (cx + 1, cy - r + 1), (cx + ear_w * 2, cy - r + 1)]
    pygame.draw.polygon(surface, COLOR_CAT, right_ear)
    pygame.draw.polygon(surface, COLOR_CAT_FACE, right_ear, 1)
    inner_right = [(cx + ear_w, cy - r - ear_h + 2), (cx + 2, cy - r), (cx + ear_w * 2 - 2, cy - r)]
    pygame.draw.polygon(surface, COLOR_CAT_FACE, inner_right)
    # Almond eyes with slit pupils
    eye_dx = r // 2
    eye_y = cy - r // 4
    eye_w, eye_h = max(4, r // 2), max(2, r // 4)
    for ex in (cx - eye_dx, cx + eye_dx):
        eye_rect = pygame.Rect(ex - eye_w // 2, eye_y - eye_h // 2, eye_w, eye_h)
        pygame.draw.ellipse(surface, (255, 240, 200), eye_rect)  # light eye
        pygame.draw.ellipse(surface, COLOR_CAT_FACE, eye_rect, 1)
        # Vertical slit pupil
        slit_w = max(1, eye_w // 4)
        slit_rect = pygame.Rect(ex - slit_w // 2, eye_y - eye_h, slit_w, eye_h * 2)
        pygame.draw.ellipse(surface, COLOR_CAT_FACE, slit_rect)
    # Nose (small triangle)
    nose_y = cy + r // 4
    nose_h = max(2, r // 6)
    nose = [(cx, nose_y + nose_h), (cx - nose_h, nose_y), (cx + nose_h, nose_y)]
    pygame.draw.polygon(surface, COLOR_CAT_FACE, nose)
    pygame.draw.polygon(surface, (80, 50, 30), nose, 1)
    # Mouth: two short lines from nose corners
    mouth_y = nose_y + nose_h
    pygame.draw.line(surface, COLOR_CAT_FACE, (cx - nose_h, nose_y), (cx - nose_h // 2, mouth_y + 1), 1)
    pygame.draw.line(surface, COLOR_CAT_FACE, (cx + nose_h, nose_y), (cx + nose_h // 2, mouth_y + 1), 1)
    # Whiskers
    wx = eye_dx + r // 3
    for dy in (-1, 0, 1):
        sy = nose_y + dy
        pygame.draw.line(surface, COLOR_WHISKER, (cx - nose_h, sy), (cx - wx, sy), 1)
        pygame.draw.line(surface, COLOR_WHISKER, (cx + nose_h, sy), (cx + wx, sy), 1)


def _draw_mouse(surface: "pygame.Surface", rect: "pygame.Rect") -> None:
    cx, cy = rect.centerx, rect.centery
    r = min(rect.w, rect.h) // 2 - 4
    pygame.draw.circle(surface, COLOR_MOUSE, (cx, cy), r)
    # Ears (small circles above)
    ear_y = cy - r
    pygame.draw.circle(surface, COLOR_MOUSE, (cx - r // 2, ear_y), r // 3)
    pygame.draw.circle(surface, COLOR_MOUSE, (cx + r // 2, ear_y), r // 3)
    # Eyes
    eye_r = max(1, r // 6)
    pygame.draw.circle(surface, COLOR_MOUSE_FACE, (cx - r // 3, cy - r // 4), eye_r)
    pygame.draw.circle(surface, COLOR_MOUSE_FACE, (cx + r // 3, cy - r // 4), eye_r)


def _draw_grid(surface: "pygame.Surface", state: GameState) -> None:
    grid = state.grid
    cat_pos = state.cat.position
    mouse_pos = state.mouse.position

    for r in range(ROWS):
        for c in range(COLS):
            pos = Position(r, c)
            rect = _cell_rect(r, c)
            _draw_empty(surface, rect)
            if pos == cat_pos:
                _draw_cat(surface, rect)
            elif pos == mouse_pos:
                _draw_mouse(surface, rect)
            elif pos in grid.obstacles:
                _draw_obstacle(surface, rect)

    # Grid lines
    for c in range(COLS + 1):
        x = c * CELL_SIZE
        pygame.draw.line(surface, COLOR_GRID_LINE, (x, 0), (x, GRID_HEIGHT))
    for r in range(ROWS + 1):
        y = r * CELL_SIZE
        pygame.draw.line(surface, COLOR_GRID_LINE, (0, y), (GRID_WIDTH, y))


# Key repeat when holding a direction: initial delay (ms), then interval (ms)
KEY_REPEAT_DELAY = 100
KEY_REPEAT_INTERVAL = 50


def _draw_overlay(surface: "pygame.Surface", font: "pygame.font.Font", lines: list[str], title: str) -> None:
    """Draw a centered overlay panel with title and lines of text."""
    pad = 24
    line_h = font.get_height() + 2
    max_w = max((font.size(line)[0] for line in lines), default=0)
    box_w = max(max_w, font.size(title)[0]) + pad * 2
    box_h = line_h * (1 + len(lines)) + pad * 2 + font.get_height()
    box = pygame.Rect((WINDOW_WIDTH - box_w) // 2, (WINDOW_HEIGHT - box_h) // 2, box_w, box_h)
    overlay = pygame.Surface((box_w, box_h))
    overlay.fill(COLOR_STATUS_BG)
    pygame.draw.rect(overlay, COLOR_GRID_LINE, overlay.get_rect(), 2)
    y = pad
    title_surf = font.render(title, True, COLOR_WIN)
    overlay.blit(title_surf, ((box_w - title_surf.get_width()) // 2, y))
    y += font.get_height() + 8
    for line in lines:
        surf = font.render(line, True, COLOR_STATUS_TEXT)
        overlay.blit(surf, (pad, y))
        y += line_h
    surface.blit(overlay, box.topleft)


def run_pygame_ui(seed: int = 0) -> None:
    """Run the game in a Pygame window. WASD/arrows move, N=new game, Q=quit. Hold a key to keep moving."""
    pygame.init()
    pygame.key.set_repeat(KEY_REPEAT_DELAY, KEY_REPEAT_INTERVAL)
    pygame.display.set_caption("Cat Chase Mouse")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    status_font = pygame.font.Font(None, 24)
    state = create_game(seed)
    status_msg = ""
    move_count = 0
    won_initials_done = False
    initials_buffer = ""
    show_leaderboard_overlay = False
    leaderboard_close_on_any_key = False

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if show_leaderboard_overlay and leaderboard_close_on_any_key:
                    show_leaderboard_overlay = False
                    continue
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
                    break
                if event.key in (pygame.K_n, pygame.K_r):
                    seed = random.randint(0, 2**31 - 1)
                    state = create_game(seed)
                    status_msg = ""
                    move_count = 0
                    won_initials_done = False
                    initials_buffer = ""
                    show_leaderboard_overlay = False
                    continue
                if state.status == "won" and not won_initials_done:
                    if event.unicode and event.unicode.isalpha() and len(initials_buffer) < 4:
                        initials_buffer = (initials_buffer + event.unicode).upper()[:4]
                    elif event.key == pygame.K_BACKSPACE:
                        initials_buffer = initials_buffer[:-1]
                    if len(initials_buffer) == 4:
                        add_score(initials_buffer, move_count)
                        won_initials_done = True
                        show_leaderboard_overlay = True
                        leaderboard_close_on_any_key = False
                    continue
                if state.status == "won":
                    continue
                if event.key == pygame.K_l:
                    show_leaderboard_overlay = True
                    leaderboard_close_on_any_key = True
                    continue
                direction = KEY_TO_DIR.get(event.key)
                if direction:
                    result = apply_move(state, direction)
                    if result.success:
                        state = result.state
                        move_count += 1
                        status_msg = state.message if state.status == "won" else ""
                    else:
                        status_msg = result.message or "Invalid move"

        screen.fill(COLOR_EMPTY)
        _draw_grid(screen, state)

        # Status bar
        status_rect = pygame.Rect(0, GRID_HEIGHT, WINDOW_WIDTH, STATUS_HEIGHT)
        pygame.draw.rect(screen, COLOR_STATUS_BG, status_rect)
        if state.status == "won":
            text = status_msg or "You won!  N = New game   Q = Quit"
            color = COLOR_WIN
        else:
            text = status_msg or "WASD / Arrows: move   N: New game   L: Leaderboard   Q: Quit"
            color = COLOR_STATUS_TEXT
        text_surface = status_font.render(text, True, color)
        screen.blit(text_surface, (8, GRID_HEIGHT + 8))
        # Move counter (right-aligned)
        moves_text = f"Moves: {move_count}"
        moves_surface = status_font.render(moves_text, True, COLOR_STATUS_TEXT)
        screen.blit(moves_surface, (WINDOW_WIDTH - moves_surface.get_width() - 8, GRID_HEIGHT + 8))

        # Overlays
        if state.status == "won" and not won_initials_done:
            initials_display = (initials_buffer + "____")[:4]
            _draw_overlay(screen, status_font, [f"You won in {move_count} moves!", f"Enter 4 initials: {initials_display}"], "Record your score")
        elif show_leaderboard_overlay:
            top10 = get_top10()
            lines = [f"{i}. {name}   {moves} moves" for i, (name, moves) in enumerate(top10, 1)]
            if not lines:
                lines = ["No scores yet."]
            if leaderboard_close_on_any_key:
                lines.append("")
                lines.append("Press any key to close")
            else:
                lines.append("")
                lines.append("N = New game   Q = Quit")
            _draw_overlay(screen, status_font, lines, "TOP 10")

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit(0)

"""Render game state as text grid. Supports plain text (C, M, #) or emoji clipart (cat, mouse, obstacle)."""

from catgame.models import GameState, Position, ROWS, COLS

# Plain: one character per cell, works everywhere. Empty = unicode block.
TEXT_CAT = "C"
TEXT_MOUSE = "M"
TEXT_OBSTACLE = "#"
TEXT_EMPTY = "\N{full block}"  # █

# Emoji "clipart" – cat, mouse, rock/brick. Each cell is 2 display columns so the grid doesn't shift.
# Emoji are double-width; empty is padded to 2 columns (space + block).
EMOJI_CAT = "\N{cat face}"           # 🐱 (2 cols)
EMOJI_MOUSE = "\N{mouse face}"       # 🐭 (2 cols)
EMOJI_OBSTACLE = "\N{brick}"         # 🧱 (2 cols)
EMOJI_EMPTY = " \N{full block}"      # " █" (1+1 cols) so cell matches emoji width


def render_grid(state: GameState, use_emoji: bool = False) -> str:
    """Return a text grid (ROWS x COLS). use_emoji=True uses cat/mouse/brick emoji with fixed cell width."""
    grid = state.grid
    cat_pos = state.cat.position
    mouse_pos = state.mouse.position
    cat_s, mouse_s, obst_s, empty_s = (
        (EMOJI_CAT, EMOJI_MOUSE, EMOJI_OBSTACLE, EMOJI_EMPTY)
        if use_emoji
        else (TEXT_CAT, TEXT_MOUSE, TEXT_OBSTACLE, TEXT_EMPTY)
    )
    lines: list[str] = []
    for r in range(ROWS):
        row_chars: list[str] = []
        for c in range(COLS):
            pos = Position(r, c)
            if pos == cat_pos:
                row_chars.append(cat_s)
            elif pos == mouse_pos:
                row_chars.append(mouse_s)
            elif pos in grid.obstacles:
                row_chars.append(obst_s)
            else:
                row_chars.append(empty_s)
        lines.append("".join(row_chars))
    return "\n".join(lines)

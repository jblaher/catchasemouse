"""Single-window UI: grid only + status bar at bottom. Uses curses."""

import random
import sys

from catgame.cli.render import render_grid
from catgame.models import ROWS
from catgame.game.turn import apply_move
from catgame.placement.placement import create_game

try:
    import curses
    _CURSES_AVAILABLE = True
except ImportError:
    curses = None
    _CURSES_AVAILABLE = False

KEY_TO_DIR = {"w": "up", "W": "up", "s": "down", "S": "down", "a": "left", "A": "left", "d": "right", "D": "right"}


# Color pair index for grid background (matches empty cell so frame doesn't look different)
_PAIR_GRID_BG = 1


def _run_curses(stdscr, initial_seed: int, use_emoji: bool = False) -> None:
    curses.curs_set(0)
    # Match frame background to empty cells so the grid area and empty spaces look the same
    grid_attr = 0
    try:
        curses.start_color()
        try:
            curses.use_default_colors()
            curses.init_pair(_PAIR_GRID_BG, -1, -1)  # default fg, default bg
        except (curses.error, AttributeError):
            curses.init_pair(_PAIR_GRID_BG, curses.COLOR_WHITE, curses.COLOR_BLACK)
        stdscr.bkgd(" ", curses.color_pair(_PAIR_GRID_BG))
        grid_attr = curses.color_pair(_PAIR_GRID_BG)
    except curses.error:
        pass
    stdscr.clear()
    stdscr.refresh()

    seed = initial_seed
    state = create_game(seed)
    status_msg = ""

    def redraw() -> None:
        stdscr.clear()
        grid_text = render_grid(state, use_emoji=use_emoji)
        for i, line in enumerate(grid_text.split("\n")):
            try:
                stdscr.addstr(i, 0, line, grid_attr)
            except curses.error:
                pass
        # Status bar at bottom (row ROWS): errors or win message; else short hint
        if status_msg:
            bar = status_msg[: stdscr.getmaxx() - 1]
        elif state.status == "won":
            bar = "You won! N = new game  Q = quit"
        else:
            bar = "WASD / Arrows: move   N: new   Q: quit"
        try:
            stdscr.addstr(ROWS, 0, bar.ljust(stdscr.getmaxx() - 1)[: stdscr.getmaxx() - 1], curses.A_REVERSE)
        except curses.error:
            pass
        stdscr.refresh()

    redraw()

    while True:
        key = stdscr.getch()
        if key == ord("q") or key == ord("Q"):
            break
        if key == ord("n") or key == ord("r") or key == ord("N") or key == ord("R"):
            seed = random.randint(0, 2**31 - 1)
            state = create_game(seed)
            status_msg = ""
            redraw()
            continue
        # Arrow keys (curses constants)
        if key == curses.KEY_UP:
            direction = "up"
        elif key == curses.KEY_DOWN:
            direction = "down"
        elif key == curses.KEY_LEFT:
            direction = "left"
        elif key == curses.KEY_RIGHT:
            direction = "right"
        elif key in (ord(c) for c in KEY_TO_DIR):
            direction = KEY_TO_DIR.get(chr(key), "")
        else:
            continue

        if state.status == "won":
            status_msg = "Game over. N = new game, Q = quit"
            redraw()
            continue

        result = apply_move(state, direction)
        if result.success:
            state = result.state
            status_msg = state.message if state.status == "won" else ""
        else:
            status_msg = result.message or "Invalid move"
        redraw()


def run_curses_ui(seed: int, use_emoji: bool = False) -> None:
    """Run the game in a single curses window (grid + status bar only)."""
    if not _CURSES_AVAILABLE:
        raise RuntimeError("curses not available")
    if not sys.stdin.isatty():
        raise RuntimeError("curses UI requires a TTY")
    try:
        curses.wrapper(_run_curses, seed, use_emoji)
    except KeyboardInterrupt:
        pass

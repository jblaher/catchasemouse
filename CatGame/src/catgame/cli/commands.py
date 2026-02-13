"""Command loop: parse up/down/left/right, call apply_move, print state or stderr feedback."""

import json
import logging
import random
import sys

try:
    import tty
    import termios
    _RAW_KEYS_AVAILABLE = True
except ImportError:
    _RAW_KEYS_AVAILABLE = False

from catgame.cli.render import render_grid
from catgame.cli.curses_ui import _CURSES_AVAILABLE, run_curses_ui
from catgame.game.turn import apply_move
from catgame.models import GameState
from catgame.placement.placement import create_game

logger = logging.getLogger(__name__)
INVALID_MESSAGE = "Invalid move"

COMMANDS_HELP = """
Commands:
  up, down, left, right   Move the cat one cell
  W, A, S, D             Same as up, left, down, right (with Enter)
  Arrow keys             Same as up/left/down/right (with Enter, or use --keys for one key per move)
  state                  Show the current grid
  new, restart           Start a new game
  quit, exit             End the game

Run with --keys to use W/A/S/D and arrow keys without pressing Enter (q=quit, n/r=new game).
"""

# Map key / line input to direction (up, down, left, right)
KEY_TO_DIRECTION = {
    "up": "up", "w": "up",
    "down": "down", "s": "down",
    "left": "left", "a": "left",
    "right": "right", "d": "right",
    # Arrow key escape sequences (when read as a line)
    "\x1b[A": "up", "\x1bOA": "up",   # Up
    "\x1b[B": "down", "\x1bOB": "down",  # Down
    "\x1b[D": "left", "\x1bOD": "left",  # Left
    "\x1b[C": "right", "\x1bOC": "right",  # Right
}


def _key_to_direction(cmd: str) -> str | None:
    """Return direction (up/down/left/right) or None if not a move key."""
    key = cmd.strip()
    return KEY_TO_DIRECTION.get(key) or KEY_TO_DIRECTION.get(key.lower())


def _read_key() -> str:
    """Read a single key (for raw mode). Handles arrow escape sequences."""
    if not _RAW_KEYS_AVAILABLE:
        return ""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":  # Escape - read 2 more for arrow keys
            c2 = sys.stdin.read(1)
            c3 = sys.stdin.read(1) if c2 in ("[", "O") else ""
            if c2 == "[" and c3 in ("A", "B", "C", "D"):
                return {"A": "up", "B": "down", "D": "left", "C": "right"}[c3]
            if c2 == "O" and c3 in ("A", "B", "C", "D"):
                return {"A": "up", "B": "down", "D": "left", "C": "right"}[c3]
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _print_json_state(state: GameState) -> None:
    obj = {
        "status": state.status,
        "message": state.message or "",
        "grid_size": [20, 30],
        "cat": [state.cat.position.row, state.cat.position.col],
        "mouse": [state.mouse.position.row, state.mouse.position.col],
        "obstacles": [[p.row, p.col] for p in state.grid.obstacles],
        "seed": state.seed,
    }
    print(json.dumps(obj), flush=True)


def run_loop(seed: int, use_json: bool = False, use_keys: bool = False, use_emoji: bool = False) -> None:
    # Single-window UI (grid + status bar only) when --keys and TTY and curses available
    if use_keys and _CURSES_AVAILABLE and sys.stdin.isatty() and not use_json:
        try:
            run_curses_ui(seed, use_emoji=use_emoji)
            return
        except Exception as e:
            logger.debug("Curses UI failed, falling back to key mode: %s", e)

    state = create_game(seed)
    if use_json:
        _print_json_state(state)
    else:
        print(COMMANDS_HELP.strip())
        print()
        print(render_grid(state, use_emoji=use_emoji))
        print(f"Status: {state.status}", flush=True)

    use_raw_keys = use_keys and _RAW_KEYS_AVAILABLE and sys.stdin.isatty()

    while True:
        if use_raw_keys:
            key = _read_key()
            cmd = key if isinstance(key, str) and len(key) > 1 else (key.lower() if key else "")
            # In key mode: q=quit, n/r=new game, wasd/arrows=move
            if cmd == "q":
                break
            if cmd in ("n", "r"):
                new_seed = random.randint(0, 2**31 - 1)
                logger.info("New game (seed=%s)", new_seed)
                state = create_game(new_seed)
                if not use_json:
                    print(render_grid(state, use_emoji=use_emoji))
                    print(f"Status: {state.status}", flush=True)
                continue
        else:
            line = sys.stdin.readline()
            if not line:
                break
            cmd = line.strip().lower()
        if not use_raw_keys and cmd in ("quit", "exit"):
            break
        if not use_raw_keys and cmd in ("new", "restart"):
            new_seed = random.randint(0, 2**31 - 1)
            logger.info("New game (seed=%s)", new_seed)
            state = create_game(new_seed)
            if use_json:
                _print_json_state(state)
            else:
                print(render_grid(state, use_emoji=use_emoji))
                print(f"Status: {state.status}", flush=True)
            continue
        if not use_raw_keys and cmd == "state":
            if use_json:
                _print_json_state(state)
            else:
                print(render_grid(state, use_emoji=use_emoji))
                print(f"Status: {state.status}", flush=True)
            continue
        direction = _key_to_direction(cmd)
        if direction is not None:
            if state.status == "won":
                logger.debug("Move rejected: game already won")
                print(INVALID_MESSAGE, file=sys.stderr, flush=True)
                continue
            result = apply_move(state, direction)
            if result.success:
                state = result.state
                logger.info("Move %s applied; status=%s", direction, state.status)
                if use_json:
                    _print_json_state(state)
                else:
                    print(render_grid(state, use_emoji=use_emoji))
                    print(f"Status: {state.status}", flush=True)
                if state.status == "won":
                    logger.info("Game won: %s", state.message)
                    if not use_json:
                        print(state.message, flush=True)
            else:
                logger.debug("Invalid move: %s", result.message)
                print(result.message or INVALID_MESSAGE, file=sys.stderr, flush=True)
            continue
        if use_raw_keys and not direction:
            continue  # Ignore unknown key in key mode
        print(INVALID_MESSAGE, file=sys.stderr, flush=True)

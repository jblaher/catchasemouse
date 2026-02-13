"""Valid moves for cat or mouse: adjacent, in-bounds, not obstacle."""

from catgame.models import GameState, Position, ROWS, COLS

DIRECTION_DELTA = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}


def get_valid_moves(state: GameState, actor: str) -> list[Position]:
    """Return list of positions that are adjacent, in bounds, and not obstacles.
    For mouse, exclude current cat position.
    """
    if actor == "cat":
        current = state.cat.position
        blocked_by_actor = set()
    else:
        current = state.mouse.position
        blocked_by_actor = {state.cat.position}

    obstacles = state.grid.obstacles
    out: list[Position] = []
    for name, (dr, dc) in DIRECTION_DELTA.items():
        r, c = current.row + dr, current.col + dc
        if not (0 <= r < ROWS and 0 <= c < COLS):
            continue
        pos = Position(r, c)
        if pos in obstacles or pos in blocked_by_actor:
            continue
        out.append(pos)
    return out

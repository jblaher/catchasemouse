"""Mouse move: maximize distance from cat and escape options; deterministic tie-break. None if no valid move."""

from catgame.game.moves import get_valid_moves
from catgame.models import GameState, Mouse, Position


def choose_mouse_move(state: GameState) -> Position | None:
    """Return the best move for the mouse.
    Prefers: 1) farther from cat (Manhattan), 2) more valid moves next turn (avoid corners).
    Tie-break: row then col order. Returns None if no valid move (caller treats as win).
    """
    moves = get_valid_moves(state, "mouse")
    if not moves:
        return None
    cat_pos = state.cat.position

    def score(p: Position) -> tuple[int, int, int, int]:
        # 1) Maximize distance from cat
        dist = p.manhattan_distance(cat_pos)
        # 2) Prefer positions with more escape options next turn (avoid dead ends / corners)
        next_state = GameState(
            grid=state.grid,
            cat=state.cat,
            mouse=Mouse(p),
            seed=state.seed,
            status="playing",
            message="",
        )
        num_options = len(get_valid_moves(next_state, "mouse"))
        return (dist, num_options, -p.row, -p.col)

    return max(moves, key=score)

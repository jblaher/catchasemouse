"""Apply cat move: validate, move cat, then move mouse or win. Returns ApplyResult."""

import logging
from dataclasses import dataclass

from catgame.game.moves import DIRECTION_DELTA, get_valid_moves

logger = logging.getLogger(__name__)
from catgame.models import Cat, GameState, Mouse, Position, ROWS, COLS
from catgame.mouse_ai.ai import choose_mouse_move
from catgame.placement.placement import maybe_reshuffle_obstacles


@dataclass
class ApplyResult:
    success: bool
    state: GameState
    message: str = ""


def apply_move(state: GameState, direction: str) -> ApplyResult:
    """Apply one turn: cat moves in direction (if valid), then mouse moves or game wins.
    Invalid move => unchanged state, success=False, message with feedback.
    """
    if state.status != "playing":
        return ApplyResult(success=False, state=state, message="Game already ended.")
    direction = direction.lower().strip()
    if direction not in DIRECTION_DELTA:
        return ApplyResult(
            success=False,
            state=state,
            message="Invalid move",
        )

    dr, dc = DIRECTION_DELTA[direction]
    new_row = state.cat.position.row + dr
    new_col = state.cat.position.col + dc
    if not (0 <= new_row < ROWS and 0 <= new_col < COLS):
        return ApplyResult(
            success=False,
            state=state,
            message="Invalid move",
        )
    new_cat_pos = Position(new_row, new_col)
    if new_cat_pos in state.grid.obstacles:
        logger.debug("Invalid move: cat would move into obstacle")
        return ApplyResult(
            success=False,
            state=state,
            message="Invalid move",
        )

    logger.info("Cat move %s to %s", direction, new_cat_pos)
    # Valid cat move: cat lands on new_cat_pos; check win by catch
    if new_cat_pos == state.mouse.position:
        new_state = GameState(
            grid=state.grid,
            cat=Cat(new_cat_pos),
            mouse=state.mouse,
            seed=state.seed,
            status="won",
            message="You caught the mouse!",
        )
        logger.info("Game won: cat caught mouse")
        return ApplyResult(success=True, state=new_state, message=new_state.message)

    # Move mouse (state after cat moved)
    state_after_cat = GameState(
        grid=state.grid,
        cat=Cat(new_cat_pos),
        mouse=state.mouse,
        seed=state.seed,
        status="playing",
        message="",
    )
    mouse_moves = get_valid_moves(state_after_cat, "mouse")
    if not mouse_moves:
        logger.info("Game won: mouse trapped")
        new_state = GameState(
            grid=state.grid,
            cat=Cat(new_cat_pos),
            mouse=state.mouse,
            seed=state.seed,
            status="won",
            message="You caught the mouse!",
        )
        return ApplyResult(success=True, state=new_state, message=new_state.message)

    mouse_new = choose_mouse_move(state_after_cat)
    assert mouse_new is not None

    new_state = GameState(
        grid=state.grid,
        cat=Cat(new_cat_pos),
        mouse=Mouse(mouse_new),
        seed=state.seed,
        status="playing",
        message="",
    )
    new_state = maybe_reshuffle_obstacles(new_state)
    return ApplyResult(success=True, state=new_state, message="")

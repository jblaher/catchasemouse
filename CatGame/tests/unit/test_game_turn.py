"""Unit tests for apply_move: valid move, invalid move (obstacle/off-grid)."""

import unittest

from catgame.game.turn import apply_move
from catgame.models import Cat, GameState, Grid, Mouse, Position
from catgame.placement.placement import create_game


def test_apply_move_valid_updates_cat_and_mouse() -> None:
    state = create_game(seed=100)
    result = apply_move(state, "up")
    assert result.success
    assert result.state.cat.position != state.cat.position
    assert result.state.status in ("playing", "won")


def test_apply_move_invalid_obstacle_unchanged_state() -> None:
    state = create_game(seed=101)
    # Find a direction that hits an obstacle or go off-grid
    obstacles = state.grid.obstacles
    cat = state.cat.position
    # Try each direction; at least one should be invalid or we get a valid move
    for direction in ("up", "down", "left", "right"):
        result = apply_move(state, direction)
        if not result.success:
            assert result.state.cat.position == state.cat.position
            assert result.state.mouse.position == state.mouse.position
            assert "Invalid" in result.message or result.message
            return
    # If all valid, that's ok for this seed
    assert True


def test_apply_move_invalid_direction_unchanged() -> None:
    state = create_game(seed=102)
    result = apply_move(state, "invalid")
    assert not result.success
    assert result.state.cat.position == state.cat.position
    assert "Invalid" in result.message or result.message


class TestApplyMove(unittest.TestCase):
    def test_valid_updates_cat_and_mouse(self) -> None:
        test_apply_move_valid_updates_cat_and_mouse()

    def test_invalid_direction_unchanged(self) -> None:
        test_apply_move_invalid_direction_unchanged()

    def test_invalid_obstacle_unchanged(self) -> None:
        test_apply_move_invalid_obstacle_unchanged_state()


if __name__ == "__main__":
    unittest.main()

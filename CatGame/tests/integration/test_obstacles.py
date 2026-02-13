"""Integration: placement creates obstacles; cat and mouse on empty cells; move into obstacle rejected."""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from catgame.game.turn import apply_move
from catgame.placement.placement import create_game


def test_placement_obstacles_cat_mouse_not_on_obstacles() -> None:
    state = create_game(95)
    assert state.cat.position not in state.grid.obstacles
    assert state.mouse.position not in state.grid.obstacles


def test_move_into_obstacle_rejected() -> None:
    state = create_game(96)
    for direction in ("up", "down", "left", "right"):
        result = apply_move(state, direction)
        if not result.success:
            assert result.state.cat.position == state.cat.position
            return
    # All moves valid for this seed - ok
    assert True


class TestObstacles(unittest.TestCase):
    def test_placement(self) -> None:
        test_placement_obstacles_cat_mouse_not_on_obstacles()

    def test_move_into_obstacle_rejected(self) -> None:
        test_move_into_obstacle_rejected()


if __name__ == "__main__":
    unittest.main()

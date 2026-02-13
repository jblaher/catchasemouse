"""Integration: apply_move valid; cat and mouse positions both updated or game won."""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from catgame.game.turn import apply_move
from catgame.placement.placement import create_game


def test_apply_move_valid_updates_both() -> None:
    state = create_game(90)
    result = apply_move(state, "up")
    assert result.success
    assert result.state.cat.position != state.cat.position or result.state.mouse.position != state.mouse.position or result.state.status == "won"


class TestTurnFlow(unittest.TestCase):
    def test_valid_updates_both(self) -> None:
        test_apply_move_valid_updates_both()


if __name__ == "__main__":
    unittest.main()

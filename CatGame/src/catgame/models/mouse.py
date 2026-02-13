"""System-controlled character. One per game."""

from dataclasses import dataclass

from catgame.models.position import Position


@dataclass
class Mouse:
    """Mouse has a position on the grid."""

    position: Position

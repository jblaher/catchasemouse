"""Grid with obstacles. Obstacles block movement."""

from catgame.models.position import Position, ROWS, COLS


class Grid:
    """Playable area. width=COLS, height=ROWS; obstacles is set of Position."""

    def __init__(self, obstacles: set[Position]) -> None:
        self.width = COLS
        self.height = ROWS
        for p in obstacles:
            if not (0 <= p.row < ROWS and 0 <= p.col < COLS):
                raise ValueError(f"Obstacle out of bounds: {p}")
        self.obstacles = frozenset(obstacles)

    def is_blocked(self, pos: Position) -> bool:
        return pos in self.obstacles

    def in_bounds(self, pos: Position) -> bool:
        return 0 <= pos.row < self.width and 0 <= pos.col < self.height

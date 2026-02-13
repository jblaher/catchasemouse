"""Cell position on the grid. Row in 0..ROWS-1, col in 0..COLS-1."""

from dataclasses import dataclass

ROWS = 20
COLS = 30


@dataclass(frozen=True)
class Position:
    """A cell location on the grid. row in [0, ROWS-1], col in [0, COLS-1]."""

    row: int
    col: int

    def __post_init__(self) -> None:
        if not (0 <= self.row < ROWS and 0 <= self.col < COLS):
            raise ValueError(f"Position out of bounds: ({self.row}, {self.col})")

    def __add__(self, other: "Position") -> "Position":
        return Position(self.row + other.row, self.col + other.col)

    def manhattan_distance(self, other: "Position") -> int:
        return abs(self.row - other.row) + abs(self.col - other.col)

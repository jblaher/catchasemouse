"""Full game snapshot: grid, cat, mouse, seed, status, message."""

from dataclasses import dataclass

from catgame.models.cat import Cat
from catgame.models.grid import Grid
from catgame.models.mouse import Mouse


@dataclass
class GameState:
    """Current positions, obstacle layout, status (playing | won), optional message."""

    grid: Grid
    cat: Cat
    mouse: Mouse
    seed: int
    status: str  # "playing" | "won"
    message: str = ""

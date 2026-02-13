"""Random placement with playability guarantee and seed for reproducibility."""

import random
from collections import deque

from catgame.models import Cat, GameState, Grid, Mouse, Position, ROWS, COLS


def _adjacent(pos: Position) -> list[Position]:
    out: list[Position] = []
    for r, c in [(pos.row - 1, pos.col), (pos.row + 1, pos.col), (pos.row, pos.col - 1), (pos.row, pos.col + 1)]:
        if 0 <= r < ROWS and 0 <= c < COLS:
            out.append(Position(r, c))
    return out


def _path_exists(
    start: Position, goal: Position, obstacles: set[Position]
) -> bool:
    """BFS to see if there is a path from start to goal avoiding obstacles."""
    if start == goal:
        return True
    seen = {start}
    q: deque[Position] = deque([start])
    while q:
        p = q.popleft()
        for n in _adjacent(p):
            if n == goal:
                return True
            if n not in obstacles and n not in seen:
                seen.add(n)
                q.append(n)
    return False


def _has_valid_move(pos: Position, obstacles: set[Position], other: Position) -> bool:
    for n in _adjacent(pos):
        if n not in obstacles and n != other:
            return True
    return False


def create_game(seed: int) -> GameState:
    """Create a game with random placement. Same seed => same layout.
    Guarantees: both cat and mouse have at least one valid move; path exists between them.
    """
    rng = random.Random(seed)
    max_attempts = 5000
    for _ in range(max_attempts):
        # Place obstacles (about 10–20% of cells for more challenge)
        n_cells = ROWS * COLS
        n_obstacles = rng.randint(
            max(1, n_cells // 10),
            max(2, n_cells // 5),
        )
        obstacle_set: set[Position] = set()
        while len(obstacle_set) < n_obstacles:
            obstacle_set.add(
                Position(rng.randint(0, ROWS - 1), rng.randint(0, COLS - 1))
            )

        # Place cat and mouse on empty cells
        empty = [
            Position(r, c)
            for r in range(ROWS)
            for c in range(COLS)
            if Position(r, c) not in obstacle_set
        ]
        rng.shuffle(empty)
        if len(empty) < 2:
            continue
        cat_pos = empty[0]
        mouse_pos = empty[1]
        if cat_pos == mouse_pos:
            continue

        if not _has_valid_move(cat_pos, obstacle_set, mouse_pos):
            continue
        if not _has_valid_move(mouse_pos, obstacle_set, cat_pos):
            continue
        if not _path_exists(cat_pos, mouse_pos, obstacle_set):
            continue

        grid = Grid(obstacle_set)
        cat = Cat(cat_pos)
        mouse = Mouse(mouse_pos)
        return GameState(
            grid=grid,
            cat=cat,
            mouse=mouse,
            seed=seed,
            status="playing",
            message="",
        )

    raise RuntimeError("Could not generate playable layout within max_attempts")


# Chance each turn that some obstacles move; max number moved per reshuffle
RESHUFFLE_PROB = 0.2
RESHUFFLE_MAX = 3


def maybe_reshuffle_obstacles(state: GameState) -> GameState:
    """With RESHUFFLE_PROB chance, move 1 to RESHUFFLE_MAX obstacles to random empty cells.
    Keeps cat and mouse positions clear. Returns new state (or unchanged if no reshuffle).
    """
    if state.status != "playing":
        return state
    if random.random() >= RESHUFFLE_PROB:
        return state
    obstacles = set(state.grid.obstacles)
    if not obstacles:
        return state
    n = min(random.randint(1, RESHUFFLE_MAX), len(obstacles))
    to_remove = random.sample(list(obstacles), n)
    new_obstacles = obstacles - set(to_remove)
    # Empty = not occupied by new obstacles, cat, or mouse (includes freed cells)
    empty = [
        Position(r, c)
        for r in range(ROWS)
        for c in range(COLS)
        if Position(r, c) not in new_obstacles
        and Position(r, c) != state.cat.position
        and Position(r, c) != state.mouse.position
    ]
    if len(empty) < n:
        n = len(empty)
    if n == 0:
        return state
    new_positions = random.sample(empty, n)
    new_obstacles = new_obstacles | set(new_positions)
    new_grid = Grid(new_obstacles)
    return GameState(
        grid=new_grid,
        cat=state.cat,
        mouse=state.mouse,
        seed=state.seed,
        status=state.status,
        message=state.message,
    )

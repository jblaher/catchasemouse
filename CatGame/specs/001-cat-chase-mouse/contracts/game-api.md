# Game API Contract: Cat Chase Mouse Game

**Feature**: 001-cat-chase-mouse  
**Consumers**: CLI, tests (unit + integration)

## Module Boundary

The game core exposes a minimal API so that:

- Turn application and win detection are testable without CLI.
- Placement is testable with a fixed seed.
- Mouse AI is testable with given state.

## Public API (contract)

### create_game(seed: int) -> GameState

- **Pre**: `seed` is an integer (e.g., 32-bit signed).
- **Post**: Returns a `GameState` with status `playing`, grid 25×25, exactly one cat, one mouse, one or more obstacles. Placement must satisfy: both cat and mouse have at least one valid move; a path exists between them. Same seed always produces same initial state.
- **Errors**: May raise if placement cannot be satisfied after bounded retries (implementation-defined).

### apply_move(state: GameState, direction: str) -> ApplyResult

- **Pre**: `state.status == "playing"`; `direction` in `{"up", "down", "left", "right"}`.
- **Post**:
  - If move is valid: returns result with updated state (cat moved, then mouse moved or game won), `success=True`, `message` optional.
  - If move is invalid (obstacle or off-grid): returns result with unchanged state, `success=False`, `message` with explicit feedback (e.g., "Invalid move").
- **Side effects**: None (pure function or immutable state update).
- **Win**: If after cat move the cat is on mouse cell, or mouse has no valid move, result state has `status="won"` and appropriate message.

### get_valid_moves(state: GameState, actor: "cat" | "mouse") -> list[Position]

- **Pre**: `state` is valid; `actor` is `"cat"` or `"mouse"`.
- **Post**: Returns list of positions that are adjacent, in bounds, and not obstacles. For cat, excludes current mouse position only if it's not adjacent (no special case). For mouse, excludes current cat position and obstacles.
- **Use**: Used by CLI (to show hints if desired), tests, and mouse AI (mouse chooses among valid moves).

### Mouse AI: choose_mouse_move(state: GameState) -> Position | None

- **Pre**: `state.status == "playing"`; mouse has at least one valid move (caller may check).
- **Post**: Returns one of the valid mouse positions (adjacent, empty, in bounds, not cat). Choice MUST maximize distance from cat (e.g., Manhattan); tie-break deterministic. Returns `None` if no valid move (caller treats as win).
- **Contract test**: Given state with one clearly “safest” cell (farthest from cat), assert chosen move is that cell. Given same state twice, assert same choice (deterministic).

## Data Types (reference)

- **GameState**: See data-model.md (grid, cat, mouse, seed, status, message).
- **Position**: `(row, col)` or `{row, col}`; row, col in [0, 24].
- **ApplyResult**: `{ success: bool, state: GameState, message?: str }` (or equivalent in implementation language).

## Contract Tests (integration)

- **create_game(seed)**: For seed 1 and 2, assert different layouts; for same seed, assert identical layout twice.
- **apply_move valid**: Create game with known seed; apply one valid move; assert cat position changed, mouse position changed (or game won), state consistent.
- **apply_move invalid**: Create game; apply move into obstacle; assert state unchanged, success=False, message non-empty.
- **apply_move win by catch**: Set up state (or replay moves) so next move is cat onto mouse; apply that move; assert status=won.
- **apply_move win by trap**: Set up state so mouse has no valid move; apply any valid cat move (or no move); assert status=won.
- **choose_mouse_move**: Given state with single best move (farthest from cat), assert return equals that position; assert deterministic for same state.

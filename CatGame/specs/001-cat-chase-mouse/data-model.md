# Data Model: 2D Cat Chase Mouse Game

**Feature**: 001-cat-chase-mouse  
**Date**: 2025-02-13

## Entities

### Position

- **Purpose**: A cell location on the 25×25 grid.
- **Fields**:
  - `row`: integer, 0..24
  - `col`: integer, 0..24
- **Validation**: Both coordinates in range [0, 24]; invalid positions must be rejected at boundaries (FR-006, FR-009).
- **Relationships**: Used by Grid (cell lookup), Cat, Mouse, and Obstacle set.

### Grid

- **Purpose**: The 25×25 playable area; defines which cells are empty vs blocked.
- **Fields**:
  - `width`: 25 (constant)
  - `height`: 25 (constant)
  - `obstacles`: set of Position (cells that block movement)
- **Invariants**: Obstacles must be within bounds; cat and mouse positions are not in obstacles.
- **Relationships**: Contains obstacles; cat and mouse positions reference grid cells.

### Cat

- **Purpose**: Player-controlled character.
- **Fields**:
  - `position`: Position (current cell)
- **State transitions**: Position changes only when a valid move is applied (FR-004); invalid move leaves position unchanged and triggers feedback (FR-009).
- **Relationships**: One per game; position must be on grid and not in obstacles.

### Mouse

- **Purpose**: System-controlled character that moves each turn to avoid the cat.
- **Fields**:
  - `position`: Position (current cell)
- **State transitions**: Position changes once per turn after cat move (FR-005); if no valid move, game ends with player win (FR-007). Never moves onto cat, obstacle, or off grid.
- **Relationships**: One per game; position must be on grid and not in obstacles.

### GameState

- **Purpose**: Full snapshot of a game for display, persistence for replay, and CLI output.
- **Fields**:
  - `grid`: Grid (obstacles)
  - `cat`: Cat
  - `mouse`: Mouse
  - `seed`: integer (placement RNG seed; for reproducibility)
  - `status`: enum — `playing` | `won` (player won)
  - `message`: optional string (e.g., last invalid-move feedback or win message)
- **Invariants**: When status is `playing`, cat and mouse are on distinct cells and not on obstacles; when `won`, game is terminal until new game starts (FR-010).
- **State transitions**: `playing` → `won` when (a) cat moves onto mouse cell, or (b) mouse has no valid move. New game resets to new `playing` state with new placement (FR-010).

## Validation Rules (from requirements)

- **FR-002, FR-003**: Placement produces exactly one cat, one mouse, and one or more obstacles; both cat and mouse have at least one valid move; path exists between cat and mouse; seed determines placement.
- **FR-006**: No move (cat or mouse) may result in position in obstacles or outside 0..24.
- **FR-007**: Win when cat.position == mouse.position (after cat move) or when mouse has no empty adjacent cell.
- **FR-009**: Invalid cat move leaves GameState unchanged (except optional message for feedback).

## Glossary

- **Valid move**: A move to an adjacent cell (up/down/left/right) that is in bounds and not an obstacle.
- **Turn**: One player move (cat) followed by one mouse move (if game still playing and mouse has a valid move) or immediate win (if mouse trapped or cat lands on mouse).
- **Playability guarantee**: Initial placement such that both cat and mouse have at least one valid move and a path exists between them.

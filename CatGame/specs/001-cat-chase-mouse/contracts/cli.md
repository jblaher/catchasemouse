# CLI Contract: Cat Chase Mouse Game

**Feature**: 001-cat-chase-mouse  
**Constitution**: Runnable & Scriptable (text I/O; optional JSON)

## Invocation

- **Entrypoint**: Single executable/script (e.g., `python -m catgame.cli` or `catgame`).
- **Modes**:
  - **Interactive**: No args or `--interactive`; read commands from stdin, write to stdout/stderr.
  - **Scripted**: Optional `--seed N` for reproducible game; optional `--json` for machine-readable output.

## Commands (Interactive Mode)

Input (stdin), one command per line:

| Command | Description | Output / Side effect |
|--------|-------------|----------------------|
| `up` \| `down` \| `left` \| `right` | Move cat one cell | Grid state printed to stdout; if invalid, error message to stderr, state unchanged. |
| `state` | Print current game state | Human-readable grid + status to stdout. |
| `new` \| `restart` | Start a new game (same seed or new random) | New grid printed; game status `playing`. |
| `quit` \| `exit` | End session | Exit 0. |

Invalid command or move: message to stderr (e.g., "Invalid move" or "Can't move there"), no state change, no turn advance.

## Output Channels

- **stdout**: Grid display (text art or line-based), win message, state dump. If `--json`, one JSON object per response (see below).
- **stderr**: Error messages, invalid-move feedback. Not used for normal grid display.
- **Exit code**: 0 on normal exit (quit, win then quit); non-zero on fatal error (e.g., invalid args, I/O failure).

## JSON Output (when `--json`)

When `--json` is set, state and result lines are single-line JSON objects.

**Game state** (after move or `state`):

```json
{
  "status": "playing" | "won",
  "message": "optional string",
  "grid_size": [25, 25],
  "cat": [row, col],
  "mouse": [row, col],
  "obstacles": [[r1,c1], [r2,c2], ...],
  "seed": 12345
}
```

**Error** (on invalid move or command):

```json
{
  "error": true,
  "message": "Invalid move" 
}
```

## Contract Tests (Integration)

- **Valid move**: Send `up` (or other direction) with known state; assert stdout contains updated positions, stderr empty, exit 0 when game continues.
- **Invalid move**: Send move into obstacle or off-grid; assert stderr contains feedback message, state unchanged (e.g., `state` command shows same positions), exit 0 (game not exited).
- **Win**: Sequence of moves until cat catches mouse or mouse trapped; assert final state has `status: "won"`, message indicates win.
- **New game**: Send `new` or `restart`; assert new grid, status `playing`.
- **Seed**: Invoke with `--seed 42`; run same move sequence twice; assert identical state progression (deterministic).

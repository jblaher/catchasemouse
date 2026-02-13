# Quickstart: 2D Cat Chase Mouse Game

**Feature**: 001-cat-chase-mouse  
**Branch**: 001-cat-chase-mouse

## Prerequisites

- Python 3.11+
- No external dependencies for core game (stdlib only); optional terminal UI may use `curses` (usually built-in on Linux/macOS).

## Setup (from repository root)

```bash
# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dev dependencies (pytest, lint)
pip install pytest ruff   # or from requirements-dev.txt if added
```

## Run the game

```bash
# Interactive (from repo root)
python -m catgame.cli

# With seed for reproducible game
python -m catgame.cli --seed 42

# JSON output (for scripting/tests)
python -m catgame.cli --json --seed 42
```

**In-game commands**: `up`, `down`, `left`, `right` to move the cat; `state` to show current grid; `new` or `restart` to start a new game; `quit` or `exit` to exit.

## Run tests

From repo root with `PYTHONPATH=src` (or install package: `pip install -e .`):

```bash
# All tests (unittest - no pytest required)
PYTHONPATH=src python3 -m unittest discover -s tests -v

# Or with pytest (if installed)
PYTHONPATH=src pytest tests -v
```

## Project layout (after implementation)

```text
src/catgame/
├── models/       # Position, Grid, Cat, Mouse, GameState
├── game/         # apply_move, win detection
├── placement/    # create_game(seed), playability check
├── mouse_ai/     # choose_mouse_move
└── cli/          # entrypoint, stdin/stdout, --json
tests/
├── unit/         # per-module tests
├── integration/  # turn flow, placement, win conditions
└── contract/     # CLI I/O contract, game API contract
```

## Validation checklist

Before considering the feature done, verify:

- [ ] `python -m catgame.cli --seed 1` starts and shows 25×25 grid with cat, mouse, obstacles.
- [ ] Moving cat with `up`/`down`/`left`/`right` updates display; invalid move prints feedback to stderr and does not advance turn.
- [ ] After catching the mouse (or mouse trapped), game shows win and accepts `new` to play again.
- [ ] Same `--seed` and same move sequence produce identical behavior (deterministic).
- [ ] Single turn (cat move + mouse response) completes within 2 seconds (SC-003).
- [ ] `pytest tests` passes (unit, integration, contract).

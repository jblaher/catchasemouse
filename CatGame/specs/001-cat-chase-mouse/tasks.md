# Tasks: 2D Cat Chase Mouse Game

**Input**: Design documents from `/specs/001-cat-chase-mouse/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per constitution (Test-First, Integration Testing). Write tests first; ensure they fail before implementation.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1–US5) for story phases only
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/catgame/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per plan.md: src/catgame/ with models/, game/, placement/, mouse_ai/, cli/ and tests/ with unit/, integration/, contract/
- [x] T002 Initialize Python 3.11+ project: add pyproject.toml or setup.py with package name catgame and pytest dependency
- [x] T003 [P] Configure linting and formatting: add ruff (or flake8/black) config and run pytest from repo root in tests/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core game logic and models that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Models (data-model.md entities)

- [x] T004 [P] Create Position in src/catgame/models/position.py (row, col 0..24; validation)
- [x] T005 [P] Create Grid in src/catgame/models/grid.py (25×25, obstacles set)
- [x] T006 [P] Create Cat in src/catgame/models/cat.py (position: Position)
- [x] T007 [P] Create Mouse in src/catgame/models/mouse.py (position: Position)
- [x] T008 Create GameState in src/catgame/models/game_state.py (grid, cat, mouse, seed, status, message); export all from src/catgame/models/__init__.py

### Placement and game logic

- [x] T009 Implement create_game(seed: int) -> GameState in src/catgame/placement/placement.py with playability guarantee (path exists, both have valid move); deterministic for same seed
- [x] T010 Implement get_valid_moves(state, actor: "cat"|"mouse") in src/catgame/game/moves.py (adjacent, in-bounds, not obstacle)
- [x] T011 Implement choose_mouse_move(state) in src/catgame/mouse_ai/ai.py (maximize distance from cat; deterministic tie-break; return None if no valid move)
- [x] T012 Implement apply_move(state, direction) -> ApplyResult in src/catgame/game/turn.py (validate cat move; if invalid return success=False + message; if valid move cat then mouse or win; handle win by catch and win by trap)

**Checkpoint**: Foundation ready — create_game(seed) and apply_move(state, direction) work; user story implementation can begin

---

## Phase 3: User Story 1 - Move the Cat on the Grid (Priority: P1) 🎯 MVP

**Goal**: Player can issue move commands (up/down/left/right); cat moves one cell per turn; invalid moves get explicit feedback to stderr.

**Independent Test**: Issue move commands; verify cat position updates for valid moves; invalid move prints feedback and does not advance turn.

### Tests for User Story 1

> **NOTE**: Write these tests FIRST, ensure they FAIL before implementation

- [x] T013 [P] [US1] Contract test: CLI valid move (send "up", assert stdout has updated state, stderr empty) in tests/contract/test_cli_moves.py
- [x] T014 [P] [US1] Contract test: CLI invalid move (send move into obstacle or off-grid, assert stderr has feedback, state unchanged) in tests/contract/test_cli_moves.py
- [x] T015 [P] [US1] Unit test: apply_move valid and invalid in tests/unit/test_game_turn.py

### Implementation for User Story 1

- [x] T016 [US1] Implement CLI entrypoint in src/catgame/cli/__main__.py (argparse --seed, --json; read commands from stdin)
- [x] T017 [US1] Implement command loop: parse up/down/left/right in src/catgame/cli/commands.py; call apply_move; on invalid write feedback to stderr (e.g., "Invalid move" or "Can't move there")
- [x] T018 [US1] Wire CLI to game: create_game(seed) on start; on valid move print state to stdout; structured logging for move/error in src/catgame/cli/commands.py

**Checkpoint**: User Story 1 complete — player can move cat via CLI; invalid moves show feedback

---

## Phase 4: User Story 2 - View the Grid, Cat, Mouse, and Obstacles (Priority: P2)

**Goal**: 25×25 grid displayed with cat, mouse, and obstacles distinguishable; display updates after each turn.

**Independent Test**: Start game; verify grid 25×25 and cat/mouse/obstacles visible; after move, display shows new positions.

### Tests for User Story 2

- [x] T019 [P] [US2] Contract test: initial state shows grid with cat, mouse, obstacles in tests/contract/test_cli_display.py
- [x] T020 [P] [US2] Contract test: after move, state command or stdout shows updated positions in tests/contract/test_cli_display.py

### Implementation for User Story 2

- [x] T021 [US2] Implement render_grid(state) in src/catgame/cli/render.py (text 25×25; distinct symbols for cat, mouse, obstacle, empty)
- [x] T022 [US2] Implement "state" command: print current grid and status to stdout in src/catgame/cli/commands.py
- [x] T023 [US2] After each move (and on start), call render_grid and print to stdout in src/catgame/cli/commands.py

**Checkpoint**: User Story 2 complete — grid view and state command work

---

## Phase 5: User Story 3 - Mouse Moves to Avoid the Cat (Priority: P3)

**Goal**: After each cat move, mouse moves exactly once to a safe cell (avoids cat when possible); if no valid move, game ends with win.

**Independent Test**: Sequence of cat moves; after each, mouse position changes once (or game wins); mouse never moves onto cat or obstacle.

### Tests for User Story 3

- [x] T024 [P] [US3] Contract test: choose_mouse_move returns valid position; given state with one safest cell, assert that cell chosen; same state twice gives same result in tests/contract/test_game_api.py
- [x] T025 [P] [US3] Integration test: apply_move valid; assert cat and mouse positions both updated (or game won) in tests/integration/test_turn_flow.py

### Implementation for User Story 3

- [x] T026 [US3] (Implementation already in Foundational: choose_mouse_move and apply_move in turn.py.) Add integration test that mouse moves after cat move and does not move onto cat in tests/integration/test_turn_flow.py

**Checkpoint**: User Story 3 complete — mouse movement and contract/integration tests pass

---

## Phase 6: User Story 4 - Win When the Cat Catches the Mouse (Priority: P4)

**Goal**: Game ends and player sees win when cat catches mouse (or mouse trapped); no further moves until new game.

**Independent Test**: Move cat onto mouse (or trap mouse); assert win message and status=won; further move commands rejected until new game.

### Tests for User Story 4

- [x] T027 [P] [US4] Contract test: apply_move win by catch (cat onto mouse) and win by trap (mouse no valid move) in tests/contract/test_game_api.py
- [x] T028 [P] [US4] Contract test: CLI win flow — after win, move command rejected or ignored; "new"/"restart" starts new game in tests/contract/test_cli_win.py

### Implementation for User Story 4

- [x] T029 [US4] On win in apply_move set state.status="won" and message; in CLI when status=won print win message to stdout in src/catgame/cli/commands.py
- [x] T030 [US4] In CLI command loop, reject move commands when state.status=="won"; implement "new"/"restart" to call create_game(seed or new) and print new grid in src/catgame/cli/commands.py

**Checkpoint**: User Story 4 complete — win flow and new game work

---

## Phase 7: User Story 5 - Obstacles Block Movement (Priority: P5)

**Goal**: Cat and mouse never move into obstacles; both blocked by same obstacle set.

**Independent Test**: Attempt cat move into obstacle → rejected + feedback; mouse never chooses obstacle cell.

### Tests for User Story 5

- [x] T031 [P] [US5] Contract test: get_valid_moves never returns obstacle cells; apply_move into obstacle leaves state unchanged in tests/contract/test_game_api.py
- [x] T032 [P] [US5] Integration test: placement creates obstacles; cat and mouse start on empty cells; move into obstacle rejected in tests/integration/test_obstacles.py

### Implementation for User Story 5

- [x] T033 [US5] (Obstacle blocking already in Foundational: get_valid_moves and apply_move.) Ensure placement never puts cat/mouse on obstacles; add logging when invalid move is obstacle in src/catgame/game/turn.py

**Checkpoint**: User Story 5 complete — obstacles block both; tests pass

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, observability, and validation

- [x] T034 [P] Add structured logging for moves, win, invalid move, new game in src/catgame/game/turn.py and src/catgame/cli/commands.py
- [x] T035 [P] Add JSON output mode: when --json, print state as single-line JSON per contracts/cli.md in src/catgame/cli/commands.py
- [x] T036 Run full quickstart.md validation: pytest tests, python -m catgame.cli --seed 1, verify grid and move/win/new game; verify single turn completes within 2 seconds (SC-003)
- [x] T037 Update specs/001-cat-chase-mouse/quickstart.md if any run commands or paths changed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–7)**: All depend on Foundational
  - US1 (Phase 3): Enables CLI move + feedback
  - US2 (Phase 4): Depends on US1 for CLI loop; can be parallel with US1 if CLI skeleton exists
  - US3 (Phase 5): Core in Foundational; phase is tests
  - US4 (Phase 6): Depends on US1/US2 for CLI win and new game
  - US5 (Phase 7): Core in Foundational; phase is tests and logging
- **Polish (Phase 8)**: Depends on all user stories

### User Story Dependencies

- **US1 (P1)**: After Foundational — no other story required
- **US2 (P2)**: After Foundational; shares CLI with US1 (implement after or with US1)
- **US3 (P3)**: After Foundational — implementation done; phase is contract/integration tests
- **US4 (P4)**: After US1/US2 (CLI for win message and new game)
- **US5 (P5)**: After Foundational — implementation done; phase is tests

### Within Each User Story

- Tests written first and must fail before implementation
- Models before game/placement/mouse_ai; game logic before CLI
- Story complete before moving to next priority

### Parallel Opportunities

- Phase 1: T003 [P]
- Phase 2: T004–T007 [P] (models); T009–T011 can run after models
- Phase 3: T013–T015 [P] (tests); then T016–T018 sequential
- Phase 4: T019–T020 [P]; T021–T023
- Phase 5–7: Contract/integration tests marked [P] where different files
- Phase 8: T034, T035 [P]

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup  
2. Complete Phase 2: Foundational  
3. Complete Phase 3: User Story 1 (move cat + invalid feedback)  
4. **STOP and VALIDATE**: Run contract tests for moves; play via CLI  
5. Demo: `python -m catgame.cli --seed 1`, issue up/down/left/right

### Incremental Delivery

1. Setup + Foundational → core game runnable (create_game, apply_move from tests)  
2. US1 → move cat via CLI (MVP)  
3. US2 → view grid  
4. US3 → mouse movement (already in core; add tests)  
5. US4 → win + new game  
6. US5 → obstacle tests + logging  
7. Polish → quickstart, JSON, logging

### Parallel Team Strategy

- One developer: Phases 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 in order  
- Two developers: After Phase 2, Dev A: US1+US2+US4 (CLI), Dev B: US3+US5 (contract/integration tests) then merge and Polish

---

## Notes

- [P] = parallelizable (different files, no blocking deps)
- [USn] = task belongs to User Story n for traceability
- Every task includes file path
- Tests first per constitution (TDD); then implementation
- Commit after each task or logical group

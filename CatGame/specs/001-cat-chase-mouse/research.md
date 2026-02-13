# Research: 2D Cat Chase Mouse Game

**Feature**: 001-cat-chase-mouse  
**Date**: 2025-02-13

## 1. Language and Runtime

**Decision**: Python 3.11+

**Rationale**: Single-user terminal game with no persistence; Python gives fast iteration, strong stdlib (random, no heavy deps), and excellent test tooling (pytest). Aligns with constitution (runnable/scriptable, minimal complexity).

**Alternatives considered**: JavaScript/Node (browser or Node CLI—adds platform choice); Rust (overkill for scope); C# (heavier tooling). Rejected in favor of minimal, cross-platform CLI and testability.

## 2. Primary Dependencies and UI

**Decision**: Standard library for core logic; optional use of `curses` (or plain print) for terminal display. No web or GUI framework.

**Rationale**: Spec and constitution require runnable/scriptable (text I/O). CLI-first with deterministic output supports automation and tests. Optional terminal UI improves playability without mandating a heavy framework.

**Alternatives considered**: Web UI (adds backend/frontend scope); native GUI (platform-specific). Rejected to keep single codebase and CLI contract as primary interface.

## 3. Testing Strategy

**Decision**: pytest for unit and integration tests; contract tests for CLI (stdin/stdout/exit codes) and for game API (apply move, get state, placement).

**Rationale**: Constitution requires test-first and integration tests at boundaries. pytest is standard for Python; contract tests enforce CLI and module contracts.

**Alternatives considered**: unittest only (pytest preferred for ergonomics); no contract tests (rejected—constitution requires contract coverage).

## 4. Placement and Playability

**Decision**: Random placement with playability guarantee implemented as: generate random obstacle set and cat/mouse positions; verify (a) path exists between cat and mouse (e.g., BFS/connectivity), (b) both have at least one valid move; retry or adjust until satisfied. Seed (integer) passed to RNG for reproducibility.

**Rationale**: Spec requires random placement, path existence, and reproducible seed. No need for external solver; in-memory validation is sufficient for 25×25.

**Alternatives considered**: Fixed levels (spec requires random + seed); external level format (deferred; can add later as optional).

## 5. Mouse AI

**Decision**: Per-turn move selection: among valid adjacent cells (empty, in-bounds, not cat), choose one that maximizes distance from cat (e.g., Manhattan or Euclidean). Tie-break deterministically (e.g., row then column order).

**Rationale**: Spec says mouse “avoids the cat when possible”; distance-based flee is simple, deterministic (good for tests and replay), and sufficient for fun gameplay.

**Alternatives considered**: Pathfinding away from cat (more complex; not required); random move among safe cells (weaker challenge). Chose deterministic flee for testability and clarity.

## 6. CLI Contract (Runnable & Scriptable)

**Decision**: CLI supports: (1) interactive mode (read move commands from stdin, render to stdout, errors to stderr); (2) optional non-interactive/script mode (e.g., `--seed N`, `--move up`, output state as text or JSON). Exit code 0 on normal exit/win, non-zero on error or invalid input.

**Rationale**: Constitution requires runnable game and text I/O; scriptable usage enables tests and automation. JSON option supports tooling and contract tests.

**Alternatives considered**: GUI-only (rejected—constitution); no JSON (rejected—contract tests and tooling benefit from machine-parseable output).

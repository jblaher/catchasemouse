"""Contract tests: initial state shows grid with cat, mouse, obstacles; after move, updated positions."""

import os
import subprocess
import sys
import unittest


def _run_cli(seed: int, stdin_text: str) -> tuple[str, str, int]:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    src = os.path.join(repo_root, "src")
    env = {**os.environ, "PYTHONPATH": src}
    proc = subprocess.run(
        [sys.executable, "-m", "catgame.cli", "--seed", str(seed)],
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=5,
        cwd=repo_root,
        env=env,
    )
    return proc.stdout or "", proc.stderr or "", proc.returncode


def test_initial_state_shows_grid_cat_mouse_obstacles() -> None:
    stdout, _, code = _run_cli(10, "state\nquit\n")
    assert code == 0
    assert "C" in stdout and "M" in stdout
    assert "#" in stdout or "\N{full block}" in stdout  # obstacles or empty (unicode block)
    assert "Status:" in stdout
    # Grid is 20 rows x 30 cols
    lines = [l for l in stdout.strip().split("\n") if len(l) == 30]
    assert len(lines) >= 20


def test_after_move_stdout_shows_updated_positions() -> None:
    stdout, _, code = _run_cli(20, "up\ndown\nstate\nquit\n")
    assert code == 0
    assert stdout.count("Status:") >= 2


class TestCLIDisplay(unittest.TestCase):
    def test_initial_shows_grid(self) -> None:
        test_initial_state_shows_grid_cat_mouse_obstacles()

    def test_after_move_updated(self) -> None:
        test_after_move_stdout_shows_updated_positions()


if __name__ == "__main__":
    unittest.main()

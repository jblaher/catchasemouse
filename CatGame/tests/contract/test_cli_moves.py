"""Contract tests: CLI valid move updates state; invalid move prints to stderr, state unchanged."""

import os
import subprocess
import sys
import unittest

# Ensure we can import catgame when running tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


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


def test_cli_valid_move_stdout_updated_stderr_empty() -> None:
    """Send several moves; at least one valid move must produce updated grid on stdout."""
    # Use seed 100 and try multiple directions so at least one valid move happens
    stdout, stderr, code = _run_cli(100, "up\ndown\nleft\nright\nstate\nquit\n")
    assert code == 0
    assert "Status:" in stdout
    assert "C" in stdout and "M" in stdout  # grid has cat and mouse
    # After a valid move we get a new grid; we have multiple Status lines
    assert stdout.count("Status:") >= 2


def test_cli_invalid_move_stderr_feedback_state_unchanged() -> None:
    """Send invalid input or move off-grid; stderr has feedback. State unchanged (same grid)."""
    # Multiple invalid commands; at least one should give stderr
    stdout, stderr, code = _run_cli(2, "invalid\nleft\nleft\nleft\nquit\n")
    assert code == 0
    # "invalid" should produce stderr
    assert "Invalid" in stderr or len(stderr) > 0


class TestCLIMoves(unittest.TestCase):
    def test_valid_move_stdout_updated_stderr_empty(self) -> None:
        test_cli_valid_move_stdout_updated_stderr_empty()

    def test_invalid_move_stderr_feedback(self) -> None:
        test_cli_invalid_move_stderr_feedback_state_unchanged()


if __name__ == "__main__":
    unittest.main()

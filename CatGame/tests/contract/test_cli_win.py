"""Contract tests: after win, move rejected; new/restart starts new game."""

import os
import subprocess
import sys
import unittest

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
        timeout=10,
        cwd=repo_root,
        env=env,
    )
    return proc.stdout or "", proc.stderr or "", proc.returncode


def test_after_win_move_rejected() -> None:
    # Play until win (many moves) then send "up" and expect stderr
    stdout, stderr, code = _run_cli(80, "up\nup\nup\ndown\ndown\nleft\nright\n" * 20 + "up\nquit\n")
    assert code == 0
    if "You caught" in stdout:
        assert "Invalid" in stderr  # the "up" after win should be rejected


def test_new_restart_starts_new_game() -> None:
    stdout, _, code = _run_cli(81, "state\nnew\nstate\nquit\n")
    assert code == 0
    assert stdout.count("Status:") >= 2


class TestCLIWin(unittest.TestCase):
    def test_win_then_move_rejected(self) -> None:
        test_after_win_move_rejected()

    def test_new_restart(self) -> None:
        test_new_restart_starts_new_game()


if __name__ == "__main__":
    unittest.main()

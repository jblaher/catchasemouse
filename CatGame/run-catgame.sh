#!/usr/bin/env bash
# One-click run script for Cat Chase Mouse game.
# Uses --keys (curses single-window UI) and --emoji (cat/mouse/brick clipart).
# When stdin is not a TTY (e.g. launched from apps menu), run under a PTY so the game uses the single-frame curses UI.
# Pass optional args (e.g. --seed 42) after the script name.
cd "$(dirname "$0")"
export PYTHONPATH="$PWD/src"
if [ ! -t 0 ]; then
  exec python3 -c 'import sys, pty; pty.spawn([sys.executable, "-m", "catgame.cli", "--keys", "--emoji"])'
else
  exec python3 -m catgame.cli --keys --emoji "$@"
fi

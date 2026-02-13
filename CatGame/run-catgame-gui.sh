#!/usr/bin/env bash
# Launch Cat Chase Mouse in the Pygame GUI window.
# Requires: pip install pygame   or   dnf install python3-pygame (Fedora)
cd "$(dirname "$0")"
export PYTHONPATH="$PWD/src"
if ! python3 -c "import pygame" 2>/dev/null; then
  echo "Pygame is not installed. Install with: pip install pygame  or  dnf install python3-pygame"
  exit 1
fi
exec python3 -m catgame.cli --gui "$@"

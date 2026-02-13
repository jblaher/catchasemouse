#!/usr/bin/env bash
# Validate desktop file and apps menu link. Run from project root.
set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
ERRORS=0

echo "=== Validating Cat Chase Mouse apps link ==="

# 1. Desktop file exists and has correct content
DESKTOP="$REPO_ROOT/CatGame.desktop"
if [ ! -f "$DESKTOP" ]; then
  echo "FAIL: CatGame.desktop not found at $DESKTOP"
  ERRORS=$((ERRORS+1))
else
  echo "OK: CatGame.desktop exists"
  if ! grep -q 'Categories=Game;' "$DESKTOP"; then
    echo "FAIL: Desktop file should contain Categories=Game; (so it appears under Games, not Other)"
    ERRORS=$((ERRORS+1))
  else
    echo "OK: Categories=Game; present (app will show in Games menu)"
  fi
  if ! grep -q 'Exec=' "$DESKTOP"; then
    echo "FAIL: Desktop file has no Exec= line"
    ERRORS=$((ERRORS+1))
  else
    echo "OK: Exec= line present"
  fi
fi

# 2. Launch script exists
SCRIPT="$REPO_ROOT/run-catgame-gui.sh"
if [ ! -f "$SCRIPT" ]; then
  echo "FAIL: run-catgame-gui.sh not found"
  ERRORS=$((ERRORS+1))
else
  echo "OK: run-catgame-gui.sh exists"
  if [ ! -x "$SCRIPT" ]; then
    echo "WARN: run-catgame-gui.sh is not executable (chmod +x $SCRIPT)"
  fi
fi

# 3. Pygame / GUI validation
export PYTHONPATH="$REPO_ROOT/src"
if ! python3 -c "import pygame" 2>/dev/null; then
  echo "FAIL: Pygame is not installed. Install with: pip install pygame  or  dnf install python3-pygame"
  ERRORS=$((ERRORS+1))
else
  echo "OK: Pygame is installed"
fi

if [ $ERRORS -gt 0 ]; then
  echo ""
  echo "Validation failed with $ERRORS issue(s). Fix the above and run again."
  exit 1
fi

echo ""
echo "=== All checks passed ==="
echo "To install/update the apps menu link, run:"
echo "  cp $DESKTOP ~/.local/share/applications/"
echo "  update-desktop-database ~/.local/share/applications/"
echo "Then launch 'Cat Chase Mouse' from the Games menu."
exit 0

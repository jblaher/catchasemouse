#!/usr/bin/env python3
"""Validate pygame is installed and the game can be launched in the Pygame GUI.
Run from project root: PYTHONPATH=src python3 scripts/validate_pygame_gui.py
Exit 0 if OK, non-zero and a message if not.
"""
import sys

def main():
    try:
        import pygame
    except ImportError as e:
        print("Pygame is not installed.", file=sys.stderr)
        print("Install with: pip install pygame", file=sys.stderr)
        print("On Fedora: dnf install python3-pygame", file=sys.stderr)
        return 1
    try:
        pygame.init()
        pygame.quit()
    except Exception as e:
        print("Pygame init failed:", e, file=sys.stderr)
        return 1
    try:
        from catgame.gui.pygame_ui import run_pygame_ui
    except ImportError as e:
        print("CatGame GUI module failed:", e, file=sys.stderr)
        return 1
    print("OK: pygame is installed and CatGame GUI can be launched.")
    print("Run: python3 -m catgame.cli --gui   or   ./run-catgame-gui.sh")
    return 0

if __name__ == "__main__":
    sys.exit(main())

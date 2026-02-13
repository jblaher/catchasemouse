"""CLI entrypoint: argparse --seed, --json, --gui; read commands from stdin."""

import argparse
import random
import sys

from catgame.cli.commands import run_loop


def main() -> None:
    parser = argparse.ArgumentParser(description="Cat Chase Mouse game (20x30 grid)")
    parser.add_argument("--seed", type=int, default=None, metavar="N", help="RNG seed for same map (omit for random map each run)")
    parser.add_argument("--json", action="store_true", help="Output state as JSON (future)")
    parser.add_argument("--keys", action="store_true", help="Use W/A/S/D and arrow keys (one key per move, no Enter)")
    parser.add_argument("--emoji", action="store_true", help="Use cat/mouse/brick emoji instead of C, M, #")
    parser.add_argument("--gui", action="store_true", help="Open Pygame GUI window (requires: pip install pygame)")
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else random.randint(0, 2**31 - 1)

    if args.gui:
        from catgame.gui.pygame_ui import run_pygame_ui
        run_pygame_ui(seed=seed)
        return

    run_loop(seed=seed, use_json=args.json, use_keys=args.keys, use_emoji=args.emoji)
    sys.exit(0)


if __name__ == "__main__":
    main()

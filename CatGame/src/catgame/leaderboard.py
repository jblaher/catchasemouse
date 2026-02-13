"""Persistent top-10 leaderboard by moves (lower is better). Stored on disk across runs."""

import json
import os
from pathlib import Path

LEADERBOARD_SIZE = 10


def _get_leaderboard_path() -> Path:
    """Path to leaderboard JSON file. Uses XDG_DATA_HOME or ~/.local/share."""
    base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    dir_path = Path(base) / "catgame"
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path / "leaderboard.json"


def load_leaderboard() -> list[dict]:
    """Load leaderboard from disk. Returns list of {"name": str, "moves": int}, sorted by moves ascending."""
    path = _get_leaderboard_path()
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    entries = data if isinstance(data, list) else []
    return sorted(entries, key=lambda e: (e.get("moves", 0), e.get("name", "")))


def save_leaderboard(entries: list[dict]) -> None:
    """Save leaderboard to disk. Expects list of {"name": str, "moves": int} (any order)."""
    path = _get_leaderboard_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def add_score(name: str, moves: int) -> None:
    """Add a score (4-letter name, move count). Keeps only top LEADERBOARD_SIZE (lowest moves)."""
    name = (name + "    ")[:4].strip().upper()
    if not name:
        name = "????"
    entries = load_leaderboard()
    entries.append({"name": name, "moves": moves})
    entries.sort(key=lambda e: (e["moves"], e["name"]))
    save_leaderboard(entries[:LEADERBOARD_SIZE])


def get_top10() -> list[tuple[str, int]]:
    """Return top 10 entries as [(name, moves), ...], sorted by moves ascending."""
    entries = load_leaderboard()
    return [(e.get("name", "????"), e.get("moves", 0)) for e in entries[:LEADERBOARD_SIZE]]

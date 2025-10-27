from __future__ import annotations

import json
import os
from typing import Optional


def ensure_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def load_high_score(path: str = "data/highscore.json") -> int:
    """Load high score from a JSON file; return 0 if missing/invalid."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("high_score"), int):
                return int(data["high_score"])
    except Exception:
        pass
    return 0


def save_high_score(score: int, path: str = "data/highscore.json") -> None:
    """Save high score to a JSON file (ensure directory exists)."""
    ensure_dir(path)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"high_score": int(score)}, f, ensure_ascii=False, indent=2)
    except Exception:
        # Fail silently; gameplay should continue
        pass

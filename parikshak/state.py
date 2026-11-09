import json
import os
from datetime import datetime


def fmt(seconds):
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def new_state(n, minutes):
    return {
        "created": datetime.now().isoformat(timespec="seconds"),
        "duration": int(minutes * 60),
        "elapsed": 0.0,
        "current": 1,
        "submitted": False,
        "questions": [
            {"q": i, "answer": "", "flagged": False, "time": 0.0, "visits": 0}
            for i in range(1, n + 1)
        ],
    }


def save(state, path):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1)
    os.replace(tmp, path)  # atomic, so a crash never leaves a half-written file


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def count(state, field):
    return sum(1 for q in state["questions"] if q[field])

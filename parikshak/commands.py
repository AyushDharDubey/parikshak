from .colors import ERR, INFO, OK, WARN
from .keys import DOWN, LEFT, RIGHT, UP
from .screen import grid_cols
from .state import count

SUBMIT, QUIT = "submit", "quit"


def goto(state, n):
    n = max(1, min(n, len(state["questions"])))
    if n != state["current"]:
        state["current"] = n
        state["questions"][n - 1]["visits"] += 1


def handle_arrow(state, key):
    step = {LEFT: -1, RIGHT: 1, UP: -grid_cols(), DOWN: grid_cols()}[key]
    target = state["current"] + step
    if 1 <= target <= len(state["questions"]):
        goto(state, target)


def handle(state, cmd, confirm):
    """Run one typed command. Returns ((text, kind), confirm_pending, action)."""
    qs = state["questions"]
    cur = qs[state["current"] - 1]
    raw = cmd.strip()
    low = raw.lower()

    if confirm:
        if low in ("y", "yes"):
            return ("", INFO), False, SUBMIT
        return ("Submit cancelled.", INFO), False, None

    if not raw:
        return ("", INFO), False, None

    if raw.isdigit():
        n = int(raw)
        if 1 <= n <= len(qs):
            goto(state, n)
            return (f"Jumped to Q{n}.", INFO), False, None
        return (f"No question {n} (1-{len(qs)}).", ERR), False, None

    if low in ("a", "b", "c", "d"):
        cur["answer"] = low.upper()
        goto(state, state["current"] + 1)
        return (f"Q{cur['q']} = {cur['answer']}", OK), False, None

    if low.startswith(("t ", "t:")):
        text = raw[2:].strip()
        if not text:
            return ("Usage: t <your answer text>", ERR), False, None
        cur["answer"] = text
        return (f"Q{cur['q']} = {text}", OK), False, None

    if low == "f":
        cur["flagged"] = not cur["flagged"]
        word = "flagged" if cur["flagged"] else "unflagged"
        return (f"Q{cur['q']} {word}.", WARN), False, None

    if low in ("n", "p"):
        goto(state, state["current"] + (1 if low == "n" else -1))
        return ("", INFO), False, None

    if low == "x":
        cur["answer"] = ""
        return (f"Q{cur['q']} cleared.", INFO), False, None

    if low == "s":
        left = len(qs) - count(state, "answer")
        flagged = count(state, "flagged")
        return (f"Submit with {left} unanswered, {flagged} flagged? (yes/no)", WARN), True, None

    if low == "q":
        return ("", INFO), False, QUIT

    return (f"Unknown command: {raw}", ERR), False, None

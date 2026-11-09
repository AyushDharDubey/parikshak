"""Full-screen view, redrawn in place on the alternate screen so nothing reaches scrollback."""
import shutil
import sys

from .colors import C, MSG_STYLE, paint
from .state import count, fmt

ALT_SCREEN_ON = "\033[?1049h\033[?25l"
ALT_SCREEN_OFF = "\033[?25h\033[?1049l"
CELL_W = 12

HELP1 = " a/b/c/d answer+next | t <text> custom | f flag | x clear"
HELP2 = " <num> jump | arrows / n,p move | s submit | q save&quit"


def term_size():
    width, height = shutil.get_terminal_size((80, 24))
    return max(width - 1, 20), height  # skip the last column to avoid auto-wrap


def grid_cols(width=None):
    width = width or term_size()[0]
    return max(1, (width - 1) // (CELL_W + 1))


def enter():
    sys.stdout.write(ALT_SCREEN_ON)


def leave():
    sys.stdout.write(ALT_SCREEN_OFF)
    sys.stdout.flush()


def _header(state, width):
    qs = state["questions"]
    cur = qs[state["current"] - 1]
    remaining = state["duration"] - state["elapsed"]
    answered, flagged = count(state, "answer"), count(state, "flagged")

    if remaining < 300:
        rem_style = (C.RED, C.BOLD)
    elif remaining < state["duration"] * 0.25:
        rem_style = (C.YELLOW, C.BOLD)
    else:
        rem_style = (C.GREEN, C.BOLD)

    clock = _segments(width, [
        (" EXAM TRACKER", (C.BOLD, C.CYAN)),
        (f"   Elapsed {fmt(state['elapsed'])}", (C.BLUE,)),
        (f"   Remaining {fmt(remaining)}", rem_style),
    ])
    current = (f" Q {cur['q']}/{len(qs)}  Answer: {cur['answer'] or '-'}  "
               f"Flag: {'YES' if cur['flagged'] else '-'}  "
               f"Time here: {fmt(cur['time'])} (visits {cur['visits']})")
    q_style = (C.BOLD, C.YELLOW) if cur["flagged"] else (C.BOLD,)
    stats = _segments(width, [
        (f" Answered {answered}", (C.GREEN,)),
        (" | ", ()),
        (f"Flagged {flagged}", (C.YELLOW,)),
        (" | ", ()),
        (f"Unanswered {len(qs) - answered}", (C.DIM,)),
    ])
    return [clock, paint((" " + "-" * 66)[:width], C.DIM),
            paint(current[:width], *q_style), stats, ""]


def _segments(width, parts):
    """Join colored parts, truncating the plain text to width before coloring."""
    out, used = "", 0
    for text, styles in parts:
        text = text[:max(0, width - used)]
        used += len(text)
        out += paint(text, *styles)
    return out


def _cell(q, current):
    ans = (q["answer"] or "-")[:4]
    body = f"{q['q']:>3}:{ans:<4}{'F' if q['flagged'] else ' '}"
    if q["q"] == current:
        return paint(f"[{body}]", C.REV, C.BOLD)
    if q["flagged"]:
        return paint(f" {body} ", C.YELLOW)
    if q["answer"]:
        return paint(f" {body} ", C.GREEN)
    return paint(f" {body} ", C.DIM)


def _grid(state, width, max_rows):
    cols = grid_cols(width)
    cells = [_cell(q, state["current"]) for q in state["questions"]]
    rows = [" " + " ".join(cells[i:i + cols]) for i in range(0, len(cells), cols)]
    cur_row = (state["current"] - 1) // cols
    start = min(max(0, cur_row - max_rows // 2), max(0, len(rows) - max_rows))
    return rows[start:start + max_rows]


def render(state, buf, msg):
    width, height = term_size()
    msg_text, msg_kind = msg
    head = _header(state, width)
    tail = [
        "",
        paint(HELP1[:width], C.DIM),
        paint(HELP2[:width], C.DIM),
        paint((" " + msg_text)[:width], *MSG_STYLE.get(msg_kind, ())),
        paint(" > ", C.BOLD, C.CYAN) + buf[:max(0, width - 3)],
    ]
    grid = _grid(state, width, max(1, height - len(head) - len(tail)))

    lines = head + grid + tail
    sys.stdout.write("\033[H" + "\033[K\n".join(lines) + "\033[K\033[J")
    sys.stdout.flush()

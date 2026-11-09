import csv
import os
from datetime import datetime

from .colors import C, paint
from .state import count, fmt


def summary_table(state):
    qs = state["questions"]
    width = min(max([6] + [len(q["answer"]) for q in qs]), 40)
    head = f"{'Q':>4} | {'Answer':<{width}} | Flag | {'Time':>8} | Visits"
    rule = "-" * len(head)
    rows = [
        f"{q['q']:>4} | {(q['answer'] or '-')[:width]:<{width}} | "
        f"{'F' if q['flagged'] else ' ':^4} | {fmt(q['time']):>8} | {q['visits']:>6}"
        for q in qs
    ]
    total = (f"Answered: {count(state, 'answer')}/{len(qs)}   "
             f"Flagged: {count(state, 'flagged')}   "
             f"Total time: {fmt(state['elapsed'])} of {fmt(state['duration'])}")
    return head, rule, rows, total


def print_summary(state):
    head, rule, rows, total = summary_table(state)
    print(paint(head, C.BOLD, C.CYAN))
    print(paint(rule, C.DIM))
    for q, row in zip(state["questions"], rows):
        if q["flagged"]:
            print(paint(row, C.YELLOW))
        elif q["answer"]:
            print(paint(row, C.GREEN))
        else:
            print(paint(row, C.DIM))
    print(paint(rule, C.DIM))
    print(paint(total, C.BOLD))


def export(state, state_path):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.splitext(state_path)[0]
    csv_path = f"{base}_report_{stamp}.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Question", "Answer", "Flagged", "TimeSeconds", "Time", "Visits"])
        for q in state["questions"]:
            w.writerow([q["q"], q["answer"], "Y" if q["flagged"] else "",
                        round(q["time"], 1), fmt(q["time"]), q["visits"]])

    return csv_path

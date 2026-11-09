import argparse
import os
import sys
import time

from . import screen
from .colors import C, ERR, OK, paint
from .commands import QUIT, SUBMIT, handle, handle_arrow
from .keys import ARROWS, Keys
from .report import export, print_summary
from .state import count, fmt, load, new_state, save

AUTOSAVE_EVERY = 5
TICK = 0.2
TIME_UP = "Time is up!"


def run(state, path):
    qs = state["questions"]
    qs[state["current"] - 1]["visits"] = max(1, qs[state["current"] - 1]["visits"])

    buf, confirm, action = "", False, None
    msg = ("Resumed from save." if state["elapsed"] else "Session started.", OK)
    last = last_save = time.monotonic()
    last_draw_sec = -1

    screen.enter()
    with Keys() as keys:
        screen.render(state, buf, msg)
        try:
            while action is None:
                tokens = keys.get(TICK)

                now = time.monotonic()
                dt, last = now - last, now
                state["elapsed"] += dt
                qs[state["current"] - 1]["time"] += dt

                for tok in tokens:
                    if tok in ARROWS:
                        if not confirm:
                            handle_arrow(state, tok)
                    elif tok in ("\r", "\n"):
                        msg, confirm, action = handle(state, buf, confirm)
                        buf = ""
                        save(state, path)
                        last_save = now
                        if action:
                            break
                    elif tok in ("\x7f", "\x08"):
                        buf = buf[:-1]
                    elif tok == "\x03":
                        raise KeyboardInterrupt
                    elif tok.isprintable():
                        buf += tok

                if action is None and state["elapsed"] >= state["duration"]:
                    state["elapsed"] = float(state["duration"])
                    action, msg = SUBMIT, (TIME_UP, ERR)

                if now - last_save >= AUTOSAVE_EVERY:
                    save(state, path)
                    last_save = now

                sec = int(state["elapsed"])
                if action is None and (tokens or sec != last_draw_sec):
                    screen.render(state, buf, msg)
                    last_draw_sec = sec
        except KeyboardInterrupt:
            action = QUIT
        finally:
            screen.leave()

    if action == SUBMIT:
        finish(state, path, timed_out=msg[0] == TIME_UP)
    else:
        save(state, path)
        print(paint(f"Progress saved to {path}. Run the program again to resume.", C.GREEN))


def finish(state, path, timed_out):
    state["submitted"] = True
    save(state, path)
    csv_path = export(state, path)
    if timed_out:
        print(paint("TIME IS UP - responses auto-submitted.\n", C.RED, C.BOLD))
    print_summary(state)
    print()
    print(paint("CSV report : ", C.CYAN) + csv_path)
    print(paint("State file : ", C.CYAN) + path)


def ask_int(prompt, default):
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print("  Please enter a positive whole number.")


def parse_args():
    ap = argparse.ArgumentParser(description="Console exam response tracker")
    ap.add_argument("-n", "--questions", type=int, help="number of questions")
    ap.add_argument("-m", "--minutes", type=float, help="exam duration in minutes")
    ap.add_argument("--state", default="exam_state.json", help="state file path")
    ap.add_argument("--no-color", action="store_true", help="disable colors")
    return ap.parse_args()


def main():
    args = parse_args()
    if not sys.stdin.isatty():
        sys.exit("Please run this in an interactive terminal.")
    C.on = not (args.no_color or os.environ.get("NO_COLOR"))

    state = load(args.state)
    if state and not state.get("submitted"):
        print(f"Unfinished session found in {args.state} "
              f"({fmt(state['elapsed'])} elapsed, {count(state, 'answer')} answered).")
        if input("Resume it? [Y/n]: ").strip().lower() in ("", "y", "yes"):
            run(state, args.state)
            return

    n = args.questions or ask_int("Number of questions", 100)
    minutes = args.minutes or ask_int("Duration in minutes", 120)
    state = new_state(n, minutes)
    save(state, args.state)
    run(state, args.state)

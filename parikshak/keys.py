"""Non-blocking keyboard input. Keys.get() returns a list of characters and arrow tokens."""
import os
import sys
import time
import select
import termios
import tty

UP, DOWN, LEFT, RIGHT = "<UP>", "<DOWN>", "<LEFT>", "<RIGHT>"
ARROWS = (UP, DOWN, LEFT, RIGHT)


_ESC_ARROWS = {"A": UP, "B": DOWN, "D": LEFT, "C": RIGHT}

class Keys:
    def __enter__(self):
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        return self

    def __exit__(self, *exc):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
        return False

    def get(self, timeout):
        ready, _, _ = select.select([self.fd], [], [], timeout)
        if not ready:
            return []
        data = os.read(self.fd, 64).decode("utf-8", errors="ignore")
        return _tokenize(data)

def _tokenize(data):
    tokens, i = [], 0
    while i < len(data):
        if data[i] != "\x1b":
            tokens.append(data[i])
            i += 1
            continue
        # escape sequence: ESC [ ... X  or  ESC O X
        j = i + 1
        if j < len(data) and data[j] in "[O":
            j += 1
            while j < len(data) and not (data[j].isalpha() or data[j] == "~"):
                j += 1
            if j < len(data) and data[j] in _ESC_ARROWS:
                tokens.append(_ESC_ARROWS[data[j]])
        i = j + 1
    return tokens

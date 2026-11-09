class C:
    on = True
    RESET, BOLD, DIM, REV = "\033[0m", "\033[1m", "\033[2m", "\033[7m"
    RED, GREEN, YELLOW, BLUE, CYAN = "\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[36m"


def paint(text, *styles):
    if not C.on or not styles:
        return text
    return "".join(styles) + text + C.RESET


INFO, OK, WARN, ERR = "info", "ok", "warn", "err"

MSG_STYLE = {
    INFO: (C.CYAN,),
    OK: (C.GREEN,),
    WARN: (C.YELLOW, C.BOLD),
    ERR: (C.RED, C.BOLD),
}

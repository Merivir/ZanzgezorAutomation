import os

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"


def colors_enabled():
    if os.getenv("NO_COLOR"):
        return False
    return os.getenv("PYTEST_LOG_COLORS", "1").strip().lower() not in {"0", "false", "no", "off"}


def color_text(text, color):
    if not colors_enabled():
        return text
    return f"{color}{text}{RESET}"


def bold_text(text):
    return color_text(text, BOLD)


def red_text(text):
    return color_text(text, RED + BOLD)


def green_text(text):
    return color_text(text, GREEN)


def yellow_text(text):
    return color_text(text, YELLOW)


def cyan_text(text):
    return color_text(text, CYAN)
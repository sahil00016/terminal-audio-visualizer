"""Curses color-pair IDs and initializer.  Import before any addstr calls."""

import curses

# UI pairs
CP_CYAN = 1
CP_GREEN = 2
CP_YELLOW = 3
CP_WHITE = 4
CP_HEADER = 5  # black on cyan
CP_RED = 6
CP_MAG = 7
CP_BLUE = 8

# Theme pairs
CP_BARS_LO = 10
CP_BARS_MID = 11
CP_BARS_HI = 12
CP_WAVE_FILL = 13
CP_WAVE_CREST = 14
CP_SPEC_FILL = 15
CP_SPEC_EDGE = 16
CP_MAT_HEAD = 17
CP_MAT_TRAIL = 18
CP_FIRE_HOT = 19
CP_FIRE_YEL = 20
CP_FIRE_RED = 21
CP_FIRE_DIM = 22

NEON_CPS = [CP_MAG, CP_CYAN, CP_GREEN, CP_YELLOW, CP_RED, CP_BLUE, CP_MAG, CP_CYAN]


def init_colors() -> None:
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(CP_CYAN, curses.COLOR_CYAN, -1)
    curses.init_pair(CP_GREEN, curses.COLOR_GREEN, -1)
    curses.init_pair(CP_YELLOW, curses.COLOR_YELLOW, -1)
    curses.init_pair(CP_WHITE, curses.COLOR_WHITE, -1)
    curses.init_pair(CP_HEADER, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(CP_RED, curses.COLOR_RED, -1)
    curses.init_pair(CP_MAG, curses.COLOR_MAGENTA, -1)
    curses.init_pair(CP_BLUE, curses.COLOR_BLUE, -1)
    curses.init_pair(CP_BARS_LO, curses.COLOR_GREEN, -1)
    curses.init_pair(CP_BARS_MID, curses.COLOR_YELLOW, -1)
    curses.init_pair(CP_BARS_HI, curses.COLOR_RED, -1)
    curses.init_pair(CP_WAVE_FILL, curses.COLOR_BLUE, -1)
    curses.init_pair(CP_WAVE_CREST, curses.COLOR_CYAN, -1)
    curses.init_pair(CP_SPEC_FILL, curses.COLOR_CYAN, -1)
    curses.init_pair(CP_SPEC_EDGE, curses.COLOR_WHITE, -1)
    curses.init_pair(CP_MAT_HEAD, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(CP_MAT_TRAIL, curses.COLOR_GREEN, -1)
    curses.init_pair(CP_FIRE_HOT, curses.COLOR_WHITE, -1)
    curses.init_pair(CP_FIRE_YEL, curses.COLOR_YELLOW, -1)
    curses.init_pair(CP_FIRE_RED, curses.COLOR_RED, -1)
    curses.init_pair(CP_FIRE_DIM, curses.COLOR_RED, -1)

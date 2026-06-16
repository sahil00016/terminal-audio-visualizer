"""All 6 visualizer theme renderers.  Each takes (win, y, x, w, h, bands)."""

from __future__ import annotations

import curses
import math
import random
import time

from .colors import (
    CP_BARS_HI, CP_BARS_LO, CP_BARS_MID,
    CP_FIRE_DIM, CP_FIRE_HOT, CP_FIRE_RED, CP_FIRE_YEL,
    CP_MAT_HEAD, CP_MAT_TRAIL,
    CP_SPEC_EDGE, CP_SPEC_FILL,
    CP_WAVE_CREST, CP_WAVE_FILL,
    NEON_CPS,
)
from .constants import BLOCKS, VIZ_H


def _safe_addstr(win, y: int, x: int, s: str, attr: int = 0) -> None:
    try:
        win.addstr(y, x, s, attr)
    except curses.error:
        pass


# ── Bars ──────────────────────────────────────────────────────────────────────

def draw_bars(win, y: int, x: int, w: int, h: int, bands: list[float]) -> None:
    n = min(len(bands), w)
    for i in range(n):
        val    = bands[i]
        height = max(1, int(val * h))
        if val > 0.7:
            cp = curses.color_pair(CP_BARS_HI) | curses.A_BOLD
        elif val > 0.4:
            cp = curses.color_pair(CP_BARS_MID)
        else:
            cp = curses.color_pair(CP_BARS_LO)

        for row in range(h):
            ch = BLOCKS[4] if (h - 1 - row) < height else " "
            _safe_addstr(win, y + row, x + i, ch, cp)


# ── Wave ──────────────────────────────────────────────────────────────────────

def draw_wave(win, y: int, x: int, w: int, h: int, bands: list[float]) -> None:
    mid = h // 2
    for col in range(w):
        band_i = int(col / w * len(bands))
        val    = bands[band_i]
        amp    = int(val * mid)
        for row in range(h):
            dist = abs(row - mid)
            if dist <= amp:
                if dist == amp:
                    cp = curses.color_pair(CP_WAVE_CREST) | curses.A_BOLD
                    ch = "~"
                else:
                    cp = curses.color_pair(CP_WAVE_FILL)
                    ch = "│"
            else:
                ch = " "
                cp = 0
            _safe_addstr(win, y + row, x + col, ch, cp)


# ── Spectrum ──────────────────────────────────────────────────────────────────

def draw_spectrum(win, y: int, x: int, w: int, h: int, bands: list[float]) -> None:
    for col in range(w):
        band_i = int(col / w * len(bands))
        val    = bands[band_i]
        height = max(0, int(val * h))
        for row in range(h):
            if (h - 1 - row) < height:
                frac = (h - 1 - row) / h
                if frac > 0.8:
                    cp = curses.color_pair(CP_SPEC_EDGE) | curses.A_BOLD
                    ch = "▄"
                else:
                    cp = curses.color_pair(CP_SPEC_FILL)
                    ch = "█"
            else:
                ch = " "
                cp = 0
            _safe_addstr(win, y + row, x + col, ch, cp)


# ── Matrix ────────────────────────────────────────────────────────────────────

_MATRIX_COLS: dict[int, list] = {}

def draw_matrix(win, y: int, x: int, w: int, h: int, bands: list[float]) -> None:
    from .constants import MATRIX_CHARS

    # Initialise per-column state once
    for col in range(w):
        if col not in _MATRIX_COLS:
            _MATRIX_COLS[col] = {
                "pos":   random.randint(0, h - 1),
                "speed": random.uniform(0.05, 0.2),
                "last":  0.0,
                "chars": [random.choice(MATRIX_CHARS) for _ in range(h)],
            }

    now = time.monotonic()
    for col in range(w):
        state    = _MATRIX_COLS[col]
        band_val = bands[int(col / w * len(bands))]
        speed    = state["speed"] * (1.0 + band_val * 3)

        if now - state["last"] > speed:
            state["pos"]  = (state["pos"] + 1) % h
            state["last"] = now
            idx = random.randrange(h)
            state["chars"][idx] = random.choice(MATRIX_CHARS)

        head = state["pos"]
        for row in range(h):
            ch = state["chars"][row]
            if row == head:
                cp = curses.color_pair(CP_MAT_HEAD)
            elif (head - row) % h < h // 3:
                cp = curses.color_pair(CP_MAT_TRAIL)
            else:
                ch = " "
                cp = 0
            _safe_addstr(win, y + row, x + col, ch, cp)


# ── Neon ──────────────────────────────────────────────────────────────────────

def draw_neon(win, y: int, x: int, w: int, h: int, bands: list[float]) -> None:
    mid   = h // 2
    frame = int(time.monotonic() * 4)
    for col in range(w):
        band_i = int(col / w * len(bands))
        val    = bands[band_i]
        amp    = int(val * mid)
        cp_idx = (band_i + frame) % len(NEON_CPS)
        cp     = curses.color_pair(NEON_CPS[cp_idx]) | curses.A_BOLD

        for row in range(h):
            dist = abs(row - mid)
            ch   = "▮" if dist <= amp else " "
            _safe_addstr(win, y + row, x + col, ch, cp if ch != " " else 0)


# ── Fire ──────────────────────────────────────────────────────────────────────

_fire_grid: list[list[float]] = []

def draw_fire(win, y: int, x: int, w: int, h: int, bands: list[float]) -> None:
    global _fire_grid

    rows = h + 1
    # Resize grid if terminal changed
    if len(_fire_grid) != rows or (rows > 0 and len(_fire_grid[0]) != w):
        _fire_grid = [[0.0] * w for _ in range(rows)]

    # Seed bottom row from audio bands
    for col in range(w):
        band_i = int(col / w * len(bands))
        _fire_grid[rows - 1][col] = bands[band_i] * (0.8 + random.random() * 0.2)

    # Propagate upwards
    for row in range(rows - 2, -1, -1):
        for col in range(w):
            left  = _fire_grid[row + 1][(col - 1) % w]
            here  = _fire_grid[row + 1][col]
            right = _fire_grid[row + 1][(col + 1) % w]
            avg   = (left + here + right) / 3.0
            _fire_grid[row][col] = max(0.0, avg - random.random() * 0.06)

    # Render (skip the extra seeding row at the bottom)
    for row in range(h):
        for col in range(w):
            val = _fire_grid[row][col]
            if val > 0.75:
                cp, ch = curses.color_pair(CP_FIRE_HOT) | curses.A_BOLD, "█"
            elif val > 0.5:
                cp, ch = curses.color_pair(CP_FIRE_YEL), "▓"
            elif val > 0.25:
                cp, ch = curses.color_pair(CP_FIRE_RED), "▒"
            elif val > 0.05:
                cp, ch = curses.color_pair(CP_FIRE_DIM), "░"
            else:
                cp, ch = 0, " "
            _safe_addstr(win, y + row, x + col, ch, cp)


# ── Dispatcher ────────────────────────────────────────────────────────────────

_RENDERERS = {
    "bars":     draw_bars,
    "wave":     draw_wave,
    "spectrum": draw_spectrum,
    "matrix":   draw_matrix,
    "neon":     draw_neon,
    "fire":     draw_fire,
}


def draw_theme(theme: str, win, y: int, x: int, w: int, h: int, bands: list[float]) -> None:
    renderer = _RENDERERS.get(theme, draw_bars)
    renderer(win, y, x, w, h, bands)

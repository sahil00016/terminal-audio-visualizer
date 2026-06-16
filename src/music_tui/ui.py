"""Curses TUI — playlist, visualizer, controls.

Bug fixes vs original:
- pos=0.0 falsy bug: get_pos() result kept as None until explicitly checked
- 4 IPC calls per frame: all mpv state cached once at loop top
- auto-advance: idle flag + near-end check avoids double-advancing
"""

from __future__ import annotations

import curses
import random
import time
from pathlib import Path

from .colors import CP_CYAN, CP_GREEN, CP_RED, CP_WHITE, CP_YELLOW, CP_HEADER, init_colors
from .constants import CTRL_H, HELP, THEME_LABEL, THEMES, VIZ_H
from .helpers import fmt_time, progress_bar
from .platform_ import HAS_AUDIO, IS_MAC, IS_WINDOWS
from .scanner import _display_name
from .themes import draw_theme
from .visualizer import AudioVisualizer
from .mpv import MPV


def _safe(win, y: int, x: int, s: str, attr: int = 0) -> None:
    try:
        win.addstr(y, x, s, attr)
    except curses.error:
        pass


def run(
    stdscr,
    files: list[Path],
    mpv: MPV,
    viz: AudioVisualizer,
    cfg: dict,
    start_idx: int = 0,
) -> dict:
    """Main TUI loop.  Returns updated config dict on exit."""
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(80)
    init_colors()

    selected    = start_idx
    offset      = 0
    playing_idx = -1
    shuffle     = cfg.get("shuffle", False)
    repeat      = cfg.get("repeat",  False)
    theme_idx   = THEMES.index(cfg.get("theme", "bars")) if cfg.get("theme") in THEMES else 0
    autoplay    = start_idx > 0

    def play(idx: int) -> None:
        nonlocal playing_idx, autoplay
        if 0 <= idx < len(files):
            playing_idx = idx
            autoplay    = False
            mpv.load(str(files[idx]))

    def next_track() -> None:
        if not files:
            return
        nxt = random.randrange(len(files)) if shuffle else (playing_idx + 1) % len(files)
        play(nxt)

    def prev_track() -> None:
        if not files:
            return
        play((playing_idx - 1) % len(files))

    while True:
        h, w = stdscr.getmaxyx()

        ctrl_start = max(h - CTRL_H, 0)
        div2_row   = ctrl_start - 1
        viz_start  = div2_row - VIZ_H
        div1_row   = viz_start - 1
        list_h     = max(div1_row - 1, 0)
        list_w     = w - 32 if w > 52 else w
        help_x     = list_w if w > 52 else 0

        stdscr.erase()

        # ── Header ────────────────────────────────────────────────────────────
        theme_name = THEME_LABEL[THEMES[theme_idx]]
        header     = f"  Music TUI   {theme_name} "
        _safe(stdscr, 0, 0,
              header.ljust(w)[:w],
              curses.color_pair(CP_HEADER) | curses.A_BOLD)

        # ── Playlist ──────────────────────────────────────────────────────────
        if selected < offset:
            offset = selected
        elif selected >= offset + list_h:
            offset = max(selected - list_h + 1, 0)

        for i in range(list_h):
            idx = offset + i
            row = 1 + i
            if row >= div1_row or idx >= len(files):
                break
            name   = _display_name(files[idx])[: list_w - 5]
            prefix = "▶ " if idx == playing_idx else "  "
            attr   = (curses.color_pair(CP_GREEN) | curses.A_BOLD
                      if idx == playing_idx
                      else curses.color_pair(CP_WHITE))
            if idx == selected:
                attr |= curses.A_REVERSE
            _safe(stdscr, row, 0,
                  f"{prefix}{name}".ljust(list_w - 1)[: list_w - 1], attr)

        if not files:
            _draw_empty(stdscr, w)

        # ── Help panel / narrow hint ──────────────────────────────────────────
        if w > 52:
            _safe(stdscr, 1, help_x,
                  "  Keys".ljust(w - help_x)[: w - help_x],
                  curses.color_pair(CP_CYAN) | curses.A_UNDERLINE)
            for i, (key, desc) in enumerate(HELP):
                r = 2 + i
                if r >= div1_row:
                    break
                _safe(stdscr, r, help_x,
                      f"  {key:<8} {desc}"[: w - help_x],
                      curses.color_pair(CP_WHITE))
        else:
            _safe(stdscr, 1, 0,
                  " ↑↓ nav  Enter play  Space pause  t theme  q quit"[:w - 1],
                  curses.color_pair(CP_CYAN))

        # ── Divider 1 ─────────────────────────────────────────────────────────
        if 0 <= div1_row < h:
            _safe(stdscr, div1_row, 0, "─" * w, curses.color_pair(CP_CYAN))

        # ── Cache ALL mpv state once per frame ───────────────────────────────
        idle     = mpv.get_idle()
        paused   = mpv.get_paused()
        pos      = mpv.get_pos()       # may be None OR 0.0 — do NOT coerce with `or 0`
        dur      = mpv.get_duration()
        playing  = playing_idx >= 0 and not idle

        # ── Visualizer ────────────────────────────────────────────────────────
        if viz_start >= 1 and w > 1:
            bands = viz.get_bands()
            draw_theme(THEMES[theme_idx], stdscr, viz_start, 0, max(w - 1, 1), VIZ_H, bands)

            if not HAS_AUDIO:
                hint = '  pip install "sahil-music-tui[visualizer]"  for live FFT  '
                hx   = max((w - len(hint)) // 2, 0)
                _safe(stdscr, viz_start + VIZ_H // 2, hx,
                      hint[:w - 1], curses.color_pair(CP_CYAN))

        # ── Divider 2 ─────────────────────────────────────────────────────────
        if 0 <= div2_row < h:
            _safe(stdscr, div2_row, 0, "─" * w, curses.color_pair(CP_CYAN))

        # ── Controls ──────────────────────────────────────────────────────────
        if playing and playing_idx >= 0:
            track = files[playing_idx].stem
            icon  = "⏸" if paused else "▶"
        else:
            track, icon = "—", "■"

        # Auto-advance: guard with `pos is not None` to avoid 0.0 → None confusion
        if (playing and dur and pos is not None and dur > 0
                and pos >= dur - 0.5 and not idle):
            if repeat:
                play(playing_idx)
            else:
                next_track()

        bar_w    = max(w - 20, 10)
        pos_draw = pos if pos is not None else 0.0
        bar, pct = progress_bar(pos_draw, dur, bar_w)
        flags    = (("⇀ shuffle  " if shuffle else "") + ("↺ repeat" if repeat else "")).strip()

        ctrl_lines = [
            f" {icon}  {track}",
            f"    {fmt_time(pos)} / {fmt_time(dur)}  {pct:3d}%{'  ' + flags if flags else ''}",
            f"    {bar}",
            f"    vol: +/-   mute: m   seek: ←→   theme: t",
        ]
        for i, line in enumerate(ctrl_lines):
            r = ctrl_start + i
            if r >= h:
                break
            cp = CP_YELLOW if i <= 1 else CP_WHITE
            _safe(stdscr, r, 0, line[: w - 1], curses.color_pair(cp))

        # Autoplay: triggered when opened with a specific file
        if autoplay:
            play(start_idx)

        stdscr.refresh()

        # ── Input ─────────────────────────────────────────────────────────────
        try:
            key = stdscr.getch()
        except curses.error:
            key = -1

        if key == ord("q"):
            break
        elif key in (ord("j"), curses.KEY_DOWN):
            selected = min(selected + 1, max(len(files) - 1, 0))
        elif key in (ord("k"), curses.KEY_UP):
            selected = max(selected - 1, 0)
        elif key == curses.KEY_NPAGE:
            selected = min(selected + list_h, max(len(files) - 1, 0))
        elif key == curses.KEY_PPAGE:
            selected = max(selected - list_h, 0)
        elif key in (ord("\n"), ord("\r"), curses.KEY_ENTER):
            play(selected)
        elif key == ord(" "):
            if playing_idx == -1 and files:
                play(selected)
            else:
                mpv.play_pause()
        elif key == ord("n"):
            next_track()
        elif key == ord("p"):
            prev_track()
        elif key == curses.KEY_RIGHT:
            mpv.seek(5)
        elif key == curses.KEY_LEFT:
            mpv.seek(-5)
        elif key == ord("+"):
            mpv.volume(5)
        elif key == ord("-"):
            mpv.volume(-5)
        elif key == ord("m"):
            mpv.mute()
        elif key == ord("s"):
            shuffle = not shuffle
        elif key == ord("r"):
            repeat = not repeat
        elif key == ord("t"):
            theme_idx = (theme_idx + 1) % len(THEMES)

    return {
        "theme":   THEMES[theme_idx],
        "shuffle": shuffle,
        "repeat":  repeat,
    }


def _draw_empty(stdscr, w: int) -> None:
    from .constants import AUDIO_EXTS
    if IS_WINDOWS:
        scan_paths = "  ~/Music  ~/Downloads  ~/Desktop  C:\\  D:\\ …"
    elif IS_MAC:
        scan_paths = "  ~/Music  ~/Downloads  ~/Desktop  /Volumes"
    else:
        scan_paths = "  ~/Music  ~/Downloads  ~/Desktop  ~/Documents"

    lines = [
        ("  No audio files found in:", CP_RED),
        (scan_paths, CP_YELLOW),
        ("  Supported: " + "  ".join(sorted(AUDIO_EXTS)), CP_WHITE),
    ]
    if not HAS_AUDIO:
        lines += [
            ("", CP_WHITE),
            ('  Real visualizer:  pip install "sahil-music-tui[visualizer]"', CP_CYAN),
        ]
    for i, (line, cp) in enumerate(lines):
        try:
            stdscr.addstr(3 + i, 0, line[:w - 1], curses.color_pair(cp))
        except curses.error:
            pass

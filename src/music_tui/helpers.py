"""Pure utility functions — no package-internal imports."""

from __future__ import annotations


def fmt_time(secs: float | None) -> str:
    if secs is None:
        return "--:--"
    s = int(secs)
    return f"{s // 60:02d}:{s % 60:02d}"


def progress_bar(pos: float, dur: float | None, width: int) -> tuple[str, int]:
    if dur and dur > 0:
        frac   = min(pos / dur, 1.0)
        filled = int(frac * width)
        return "█" * filled + "░" * (width - filled), int(frac * 100)
    return "░" * width, 0

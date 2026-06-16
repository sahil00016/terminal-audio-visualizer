"""music-tui entry point."""

from __future__ import annotations

import argparse
import curses
import sys
from pathlib import Path

from . import __version__
from .constants import AUDIO_EXTS
from .install import ensure_runtime_deps
from .mpv import MPV
from .scanner import install_file_association, scan_all
from .config import load as load_cfg, save as save_cfg
from .ui import run
from .visualizer import AudioVisualizer


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="music-tui",
        description="Terminal music player with visualizer. Works on Linux, macOS, Windows.",
    )
    parser.add_argument("--version", action="version", version=f"music-tui {__version__}")
    parser.add_argument(
        "file", nargs="?", type=Path,
        help="Audio file to open directly (e.g. from 'Open with…')",
    )
    args = parser.parse_args()

    # ── Pre-flight ────────────────────────────────────────────────────────────
    warnings = ensure_runtime_deps()
    for w in warnings:
        print(w)
    if any("mpv" in w for w in warnings):
        sys.exit(1)

    # Register 'Open with' handler once, silently
    install_file_association()

    # ── Scan ──────────────────────────────────────────────────────────────────
    print("Scanning for music…", end="\r", flush=True)
    files: list[Path] = scan_all()
    print("                   ", end="\r", flush=True)

    start_idx = 0
    if args.file:
        target = args.file.resolve()
        if target.suffix.lower() not in AUDIO_EXTS:
            print(f"Unsupported file format: {target.suffix}")
            print("Supported: " + "  ".join(sorted(AUDIO_EXTS)))
            sys.exit(1)
        if target not in files:
            files = [target] + files
        start_idx = files.index(target)

    # ── Load config ───────────────────────────────────────────────────────────
    cfg = load_cfg()

    # ── Launch ────────────────────────────────────────────────────────────────
    mpv = MPV()
    viz = AudioVisualizer()
    try:
        mpv.start()
    except RuntimeError as e:
        print(f"Error starting mpv: {e}")
        sys.exit(1)
    viz.start()

    try:
        updated_cfg = curses.wrapper(run, files, mpv, viz, cfg, start_idx)
        # Merge and persist any state the UI changed
        cfg.update(updated_cfg)
        save_cfg(cfg)
    finally:
        viz.stop()
        mpv.quit()

    print("Bye!")


if __name__ == "__main__":
    main()

"""File scanner and display helpers.

Bug fixes vs original:
- os.walk(followlinks=False) prevents symlink-loop infinite recursion
- except (PermissionError, OSError) catches all I/O errors mid-walk
- Windows drive enumeration uses GetLogicalDrives() bitmask (fast, no blocking probes)
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterator

from .constants import AUDIO_EXTS
from .platform_ import IS_LINUX, IS_MAC, IS_WINDOWS


# ── Scanning ─────────────────────────────────────────────────────────────────

def _scan_dirs() -> list[Path]:
    home = Path.home()
    dirs: list[Path] = [
        home / "Music",
        home / "Downloads",
        home / "Desktop",
        home / "Documents",
        home / "Videos",
    ]
    if IS_WINDOWS:
        dirs += _windows_drives()
    elif IS_LINUX:
        dirs += [
            Path("/media") / os.environ.get("USER", ""),
            Path("/mnt"),
        ]
    elif IS_MAC:
        dirs.append(Path("/Volumes"))
    return dirs


def _windows_drives() -> list[Path]:
    """Return present drive roots using a bitmask (no blocking Path.exists() probes)."""
    import string
    drives: list[Path] = []
    try:
        import ctypes
        bitmask: int = ctypes.windll.kernel32.GetLogicalDrives()
        for i, letter in enumerate(string.ascii_uppercase):
            if bitmask & (1 << i):
                drives.append(Path(f"{letter}:\\"))
    except Exception:
        # Fallback: only probe common letters
        for letter in "CDEFGH":
            p = Path(f"{letter}:\\")
            try:
                if p.exists():
                    drives.append(p)
            except OSError:
                pass
    return drives


def _iter_audio(directory: Path) -> Iterator[Path]:
    """Yield audio files under directory without following symlinks."""
    try:
        for root, _dirs, files in os.walk(str(directory), followlinks=False):
            for fname in files:
                p = Path(root) / fname
                if p.suffix.lower() in AUDIO_EXTS:
                    yield p
    except (PermissionError, OSError):
        return


def scan_all() -> list[Path]:
    seen:  set[Path] = set()
    files: list[Path] = []

    dirs = _scan_dirs()

    # Expand top-level /media/USER, /mnt, /Volumes one level (removable drives)
    expanded: list[Path] = []
    for d in dirs:
        expanded.append(d)
        if not d.exists():
            continue
        mountpoint_roots = ("/media", "/mnt", "/Volumes")
        if any(str(d).startswith(r) for r in mountpoint_roots):
            try:
                expanded += [x for x in d.iterdir() if x.is_dir()]
            except (PermissionError, OSError):
                pass

    for d in expanded:
        if not d.exists() or not d.is_dir():
            continue
        for p in _iter_audio(d):
            if p not in seen:
                seen.add(p)
                files.append(p)

    return sorted(files, key=lambda p: p.stem.lower())


def _display_name(p: Path) -> str:
    """Return 'parent/stem' so files from different folders are distinguishable."""
    parent = p.parent.name
    return f"{parent}/{p.stem}" if parent else p.stem


# ── File-manager integration ──────────────────────────────────────────────────

def install_file_association() -> None:
    """Register music-tui as an 'Open with' handler.  Runs once, silently."""
    bin_path = shutil.which("music-tui") or "music-tui"

    if IS_LINUX:
        _install_linux(bin_path)
    elif IS_WINDOWS:
        _install_windows(bin_path)
    # macOS: LaunchServices registration requires duti or a signed app bundle;
    # skip silently — users can set it manually via Finder → Get Info.


def _install_linux(bin_path: str) -> None:
    desktop_dir  = Path.home() / ".local" / "share" / "applications"
    desktop_file = desktop_dir / "music-tui.desktop"
    if desktop_file.exists():
        return
    desktop_dir.mkdir(parents=True, exist_ok=True)
    mimes = (
        "audio/mpeg;audio/flac;audio/wav;audio/ogg;audio/mp4;"
        "audio/aac;audio/opus;audio/x-ms-wma;audio/x-aiff;"
    )
    desktop_file.write_text(
        "[Desktop Entry]\n"
        "Name=Music TUI\n"
        "Comment=Terminal music player with visualizer\n"
        f"Exec={bin_path} %f\n"
        "Terminal=true\n"
        "Type=Application\n"
        "Icon=audio-x-generic\n"
        f"MimeType={mimes}\n"
        "Categories=AudioVideo;Audio;Player;\n"
    )
    for cmd in [
        ["update-desktop-database", str(desktop_dir)],
        ["xdg-mime", "default", "music-tui.desktop", "audio/mpeg"],
    ]:
        try:
            subprocess.run(cmd, capture_output=True, timeout=3)
        except Exception:
            pass


def _install_windows(bin_path: str) -> None:
    try:
        import winreg
        with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Classes\MusicTUI\shell\open\command",
        ) as k:
            winreg.SetValueEx(k, "", 0, winreg.REG_SZ, f'"{bin_path}" "%1"')
        for ext in AUDIO_EXTS:
            try:
                key_path = f"Software\\Classes\\{ext}\\OpenWithProgids"
                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE
                ) as k:
                    winreg.SetValueEx(k, "MusicTUI", 0, winreg.REG_SZ, "")
            except OSError:
                pass
    except Exception:
        pass

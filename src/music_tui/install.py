"""Dependency check and install-hint helpers."""

from __future__ import annotations

import shutil
import subprocess
import sys


def check_mpv() -> bool:
    return shutil.which("mpv") is not None


def mpv_install_hint() -> str:
    import platform
    system = platform.system()
    if system == "Linux":
        return "Install mpv:  sudo apt install mpv   (or: sudo dnf install mpv)"
    if system == "Darwin":
        return "Install mpv:  brew install mpv"
    if system == "Windows":
        return "Install mpv:  https://mpv.io/installation/ or  winget install mpv"
    return "Install mpv:  https://mpv.io/installation/"


def check_audio_deps() -> dict[str, bool]:
    """Return availability of optional audio libs."""
    result: dict[str, bool] = {}
    for mod in ("numpy", "sounddevice"):
        try:
            __import__(mod)
            result[mod] = True
        except ImportError:
            result[mod] = False
    return result


def audio_install_hint() -> str:
    return "For real audio visualization:  pip install numpy sounddevice"


def portaudio_hint() -> str:
    import platform
    system = platform.system()
    if system == "Linux":
        return "Missing PortAudio:  sudo apt install libportaudio2"
    if system == "Darwin":
        return "Missing PortAudio:  brew install portaudio"
    return "Missing PortAudio — see https://www.portaudio.com/"


def ensure_runtime_deps() -> list[str]:
    """Return a list of warning strings (empty when everything is OK)."""
    warnings: list[str] = []

    if not check_mpv():
        warnings.append(mpv_install_hint())

    audio = check_audio_deps()
    if not all(audio.values()):
        warnings.append(audio_install_hint())
    else:
        # sounddevice is present but PortAudio might still be missing
        try:
            import sounddevice as sd
            sd.query_devices()
        except OSError:
            warnings.append(portaudio_hint())
        except Exception:
            pass

    return warnings

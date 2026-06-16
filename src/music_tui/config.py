"""Persistent user config — saved to ~/.config/music-tui/config.json."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .platform_ import IS_WINDOWS

DEFAULTS: dict = {
    "theme":   "bars",
    "volume":  80,
    "shuffle": False,
    "repeat":  False,
}


def _config_path() -> Path:
    if IS_WINDOWS:
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "music-tui" / "config.json"


def load() -> dict:
    path = _config_path()
    if not path.exists():
        return dict(DEFAULTS)
    try:
        data = json.loads(path.read_text())
        return {**DEFAULTS, **{k: v for k, v in data.items() if k in DEFAULTS}}
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULTS)


def save(data: dict) -> None:
    path = _config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({k: data[k] for k in DEFAULTS if k in data}, indent=2))
    except OSError:
        pass

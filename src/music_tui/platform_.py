"""Platform detection and optional-dependency flags.

Named platform_.py (with trailing underscore) to avoid shadowing stdlib `platform`.
"""

import sys

IS_WINDOWS: bool = sys.platform == "win32"
IS_MAC: bool = sys.platform == "darwin"
IS_LINUX: bool = sys.platform == "linux"

# Windows curses shim — must be imported before any `import curses` elsewhere
if IS_WINDOWS:
    try:
        import windows_curses  # noqa: F401  patches the curses module in-place
    except ImportError as exc:
        raise ImportError(
            "windows-curses is required on Windows.\n" "Run:  pip install windows-curses"
        ) from exc

# Optional audio-capture dependencies
try:
    import numpy as np  # noqa: F401
    import sounddevice  # noqa: F401

    HAS_AUDIO: bool = True
except (ImportError, OSError):
    HAS_AUDIO: bool = False

"""Platform detection and optional-dependency flags.

Named platform_.py (with trailing underscore) to avoid shadowing stdlib `platform`.
"""

import sys

IS_WINDOWS: bool = sys.platform == "win32"
IS_MAC: bool = sys.platform == "darwin"
IS_LINUX: bool = sys.platform == "linux"

# windows-curses < 2.4 required an explicit `import windows_curses` to patch curses.
# windows-curses >= 2.4 ships a patched _curses.pyd instead — no import needed.
# Silently skip if the module no longer exists (2.4+).
if IS_WINDOWS:
    try:
        import windows_curses  # noqa: F401
    except ImportError:
        pass

# Optional audio-capture dependencies
try:
    import numpy as np  # noqa: F401
    import sounddevice  # noqa: F401

    HAS_AUDIO: bool = True
except (ImportError, OSError):
    HAS_AUDIO: bool = False

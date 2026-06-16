"""Compile-time constants — no internal imports."""

AUDIO_EXTS = frozenset({
    ".mp3", ".flac", ".wav", ".ogg", ".m4a", ".aac",
    ".opus", ".wma", ".alac", ".aiff", ".ape", ".mka",
})

VIZ_H  = 8   # visualizer rows
CTRL_H = 4   # player-controls rows

# Sub-character block glyphs (index 0–8 → empty…full)
BLOCKS = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

THEMES = ["bars", "wave", "spectrum", "matrix", "neon", "fire"]

THEME_LABEL = {
    "bars":     "▇ Bars",
    "wave":     "∿ Wave",
    "spectrum": "◈ Spectrum",
    "matrix":   "⌘ Matrix",
    "neon":     "★ Neon",
    "fire":     "▲ Fire",
}

HELP = [
    ("j / ↓",  "Move down"),
    ("k / ↑",  "Move up"),
    ("Enter",  "Play selected"),
    ("Space",  "Play / Pause"),
    ("n",      "Next track"),
    ("p",      "Prev track"),
    ("← / →", "Seek ±5 s"),
    ("+/-",    "Volume"),
    ("m",      "Mute"),
    ("s",      "Shuffle"),
    ("r",      "Repeat"),
    ("t",      "Next theme"),
    ("q",      "Quit"),
]

MATRIX_CHARS: list[str] = list("0123456789ABCDEF:;|/\\-+*#@!?><~")

# Low Level Design — terminal-audio-visualizer

## Module Reference

---

### `constants.py`

Pure literals with no imports. Frozen at import time.

```
AUDIO_EXTS : frozenset[str]   — 12 supported extensions
VIZ_H      : int = 8          — visualizer height in rows
CTRL_H     : int = 4          — controls panel height in rows
BLOCKS     : list[str]        — 9 Unicode block chars (▁–█)
THEMES     : list[str]        — ordered theme names
THEME_LABEL: dict[str, str]   — display labels with icons
HELP       : list[tuple]      — key bindings table
MATRIX_CHARS: list[str]       — characters for Matrix rain
```

---

### `platform_.py`

```
IS_WINDOWS : bool  — sys.platform == "win32"
IS_MAC     : bool  — sys.platform == "darwin"
IS_LINUX   : bool  — sys.platform == "linux"
HAS_AUDIO  : bool  — numpy + sounddevice importable
```

Windows curses shim: imports `windows_curses` which patches the stdlib
`curses` module in-place. Must happen before any `import curses`.

---

### `mpv.py`

```
class MPV:
  start()          — launches mpv subprocess, waits for IPC socket/port
  _connect()       — opens socket (AF_UNIX or AF_INET)
  _send(cmd)→any   — thread-safe JSON IPC with line-by-line buf parser
  quit()           — sends quit, waits, closes socket, rmtree(tmp_dir)

  load(path)       — loadfile replace
  play_pause()     — cycle pause
  stop()           — stop
  seek(s)          — seek relative
  volume(d)        — add volume
  mute()           — cycle mute

  get_paused()→bool|None
  get_pos()  →float|None   ← may return 0.0; never coerce with `or 0`
  get_duration()→float|None
  get_idle() →bool|None
```

IPC wire format (newline-delimited JSON):
```
→ {"command": ["get_property", "time-pos"], "request_id": 7}
← {"data": 42.3, "error": "success", "request_id": 7}
← {"event": "property-change", ...}   ← unsolicited events (ignored)
```

Response parser reads chunks until `socket.timeout`, accumulates in
`buf`, slices on `\n` with `buf.split(b"\n", 1)` to avoid losing
partial lines at the end of a recv().

Socket lifecycle:
```
Linux/macOS:  mkdtemp(prefix="music_tui_") / mpv.sock
              shutil.rmtree(tmp_dir) on quit
Windows:      TCP 127.0.0.1:<ephemeral port>
              port freed when mpv process exits
```

---

### `scanner.py`

```
scan_all() → list[Path]
  Walk order: Home subdirs → /media/USER → /mnt → /Volumes → Win drives
  Uses os.walk(followlinks=False) to prevent symlink loops
  Windows drive enumeration: GetLogicalDrives() bitmask (no blocking probes)
  Returns sorted by stem.lower()

_iter_audio(directory) → Iterator[Path]
  Yields files whose suffix is in AUDIO_EXTS
  Silently catches PermissionError / OSError per directory

_display_name(p) → str
  "parent_dir/stem"  — disambiguates same-named files in different dirs

install_file_association()
  Linux:   writes ~/.local/share/applications/music-tui.desktop
           runs update-desktop-database + xdg-mime
  Windows: writes HKCU\Software\Classes\MusicTUI registry key
  macOS:   no-op (duti requires separate install)
```

---

### `visualizer.py`

```
class AudioVisualizer(n_bands=32):
  start()          — launches daemon capture thread if HAS_AUDIO
  stop()           — sets _running=False, joins thread
  get_bands()→list[float]
    └── if max(live) < 0.01 → _fake_bands()   (silence / no audio)
    └── else returns live FFT bands normalised to [0, 1]

_capture_loop()    — daemon thread
  opens sounddevice.InputStream on PulseAudio monitor device
  FFT: np.fft.rfft on Hanning-windowed chunk
  maps FFT bins → n_bands with linear spacing
  normalises: val / peak
  updates self._bands under self._lock

_fake_bands()→list[float]
  3 overlapping sine waves with different frequencies and phases
  envelope peaks in the middle of the band array
  advances frame only every _FALLBACK_SPEED seconds
```

---

### `themes.py`

All renderers share signature:
```python
draw_XYZ(win, y: int, x: int, w: int, h: int, bands: list[float]) → None
```

| Theme | Algorithm |
|-------|-----------|
| bars | height = int(band × h); colour by threshold |
| wave | sine reflection from midpoint; crest char `~` |
| spectrum | symmetric bars from centre row outward |
| matrix | per-column drop state machine; `head/trail` chars |
| neon | same as bars but colour cycles with time+band index |
| fire | 2D cellular automaton seeded from band values at bottom row |

`draw_theme(theme, ...)` dispatches via `_RENDERERS` dict.
All `addstr` calls wrapped in `_safe_addstr` to swallow `curses.error`
at terminal edges.

---

### `config.py`

```
DEFAULTS = {theme, volume, shuffle, repeat}

load() → dict
  reads ~/.config/music-tui/config.json (XDG / %APPDATA%)
  merges: unknown keys dropped, missing keys filled from DEFAULTS
  tolerates corrupt JSON → returns DEFAULTS

save(data: dict) → None
  writes only keys present in DEFAULTS
  silently ignores OSError (read-only fs, etc.)
```

---

### `ui.py`

Layout (rows, bottom-up):
```
row 0            : header bar
rows 1..div1-1   : playlist  │  help panel (if w > 52)
row div1         : ─────────── divider 1
rows viz_start.. : visualizer (VIZ_H rows)
row div2         : ─────────── divider 2
rows ctrl_start..: controls   (CTRL_H rows)
```

Per-frame mpv state cache (avoids 4 IPC round-trips):
```python
idle   = mpv.get_idle()
paused = mpv.get_paused()
pos    = mpv.get_pos()      # None OR float (including 0.0)
dur    = mpv.get_duration()
```

Auto-advance guard:
```python
if playing and dur and pos is not None and dur > 0 and pos >= dur - 0.5 and not idle:
```
The `pos is not None` check is critical — `pos = 0.0` at track start
is valid and must not be treated the same as `None`.

`run()` returns updated `{theme, shuffle, repeat}` dict to `main()`.

---

### `install.py`

```
check_mpv() → bool                  — shutil.which("mpv")
mpv_install_hint() → str            — platform-specific install command
check_audio_deps() → dict[str,bool] — numpy + sounddevice importable?
portaudio_hint() → str              — platform-specific PortAudio install
ensure_runtime_deps() → list[str]   — combined pre-flight, returns warnings
```

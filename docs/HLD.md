# High Level Design — terminal-audio-visualizer

## Purpose

A zero-config terminal music player that:
- discovers audio files across common system locations
- streams playback through mpv (no re-encoding)
- renders a real-time audio visualizer inside a curses TUI
- persists user preferences between sessions

---

## System Context

```
┌──────────────────────────────────────────────────────────┐
│                        User                              │
│   keyboard ──► music-tui CLI ──► Terminal (curses)       │
└──────────────────────┬───────────────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │   music-tui process     │
          │                         │
          │  ┌─────────┐  ┌──────┐ │
          │  │ Scanner │  │Config│ │
          │  └────┬────┘  └──────┘ │
          │       │                 │
          │  ┌────▼────────────┐   │
          │  │   TUI / UI      │   │
          │  └─────┬──────┬────┘   │
          │        │      │         │
          │  ┌─────▼─┐  ┌─▼──────┐ │
          │  │  MPV  │  │  Viz   │ │
          │  │  IPC  │  │  FFT   │ │
          │  └───┬───┘  └───┬────┘ │
          └──────┼──────────┼──────┘
                 │          │
        ┌────────▼─┐   ┌────▼───────────┐
        │  mpv     │   │ PulseAudio /   │
        │ process  │   │ sounddevice    │
        └──────────┘   └────────────────┘
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Playback engine | mpv via IPC | Battle-tested, supports all formats, no Python audio codec deps |
| IPC transport | Unix socket (Linux/macOS), TCP (Windows) | mpv's native IPC protocol |
| Audio capture | sounddevice + numpy FFT | Captures PulseAudio monitor (system output), not mic |
| TUI framework | Python curses | stdlib, zero install on all platforms |
| Config storage | JSON at `~/.config/music-tui/` | XDG on Linux/macOS, `%APPDATA%` on Windows |
| Scanner | `os.walk(followlinks=False)` | Avoids symlink loops; scans Home + removable mounts |

---

## Data Flow

```
Startup
  main() ──► scan_all() ──► files: list[Path]
          ──► load_cfg()  ──► cfg: dict
          ──► MPV.start() ──► mpv subprocess + IPC socket
          ──► AudioVisualizer.start() ──► capture thread (daemon)
          ──► curses.wrapper(run, ...)

Main Loop (80 ms tick)
  ┌─────────────────────────────────────────────────────────┐
  │  1. stdscr.erase()                                       │
  │  2. Cache mpv state (idle / paused / pos / dur)  ← 1 IPC│
  │  3. viz.get_bands() → FFT bands OR fake animation        │
  │  4. draw: header → playlist → divider → viz → controls   │
  │  5. stdscr.refresh()                                     │
  │  6. stdscr.getch() → handle keypress                     │
  └─────────────────────────────────────────────────────────┘

Shutdown
  viz.stop() → join capture thread
  mpv.quit() → send quit IPC → wait → close socket → rmtree(tmp_dir)
  save_cfg(cfg)
```

---

## Module Dependency Graph

```
__main__
  ├── config
  ├── install
  ├── scanner ──► constants, platform_
  ├── mpv     ──► platform_
  ├── visualizer ──► platform_  (numpy/sounddevice optional)
  └── ui
        ├── colors ──► (curses)
        ├── constants
        ├── helpers
        ├── platform_
        ├── scanner (_display_name)
        ├── themes ──► colors, constants
        ├── visualizer
        └── mpv
```

---

## Non-Functional Properties

| Property | Target |
|----------|--------|
| Startup latency | < 2 s (scan + mpv IPC connect) |
| Frame rate | ~12 fps (80 ms timeout) |
| Memory | < 50 MB RSS (numpy FFT buffer is small) |
| Platforms | Linux, macOS, Windows (PowerShell / CMD) |
| Python | 3.9 — 3.12 |

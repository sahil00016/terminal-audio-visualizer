# music-tui

A terminal music player with real-time audio visualizer themes, built with Python + mpv.

```
 🎵 Music TUI   ▲ Fire
───────────────────────────────────────────────────────────────
▶ CITYWLKR - Immortal                     Keys
  Song Two                                j / ↓    Move down
  Song Three                              k / ↑    Move up
                                          Enter    Play selected
                                          Space    Play / Pause
                                          n        Next track
                                          p        Prev track
                                          ← / →   Seek ±5 s
                                          +/-      Volume
                                          m        Mute
                                          s        Shuffle
                                          r        Repeat
                                          t        Next theme
                                          q        Quit
──────────────────────────────────────────────────────────────
  ▲▲  ████ ███  ██  ████ ▲▲▲ ████  ███ ▲▲  ████ ███ ██ ████
──────────────────────────────────────────────────────────────
▶  CITYWLKR - Immortal
   01:23 / 03:45   36%
   ████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
   vol: +/-   mute: m   seek: ←→   theme: t
```

## Features

- Browse and play audio files from `~/Music` (recursive)
- Supports `.mp3`, `.flac`, `.wav`, `.ogg`, `.m4a`, `.aac`, `.opus`, `.wma`
- **6 visualizer themes** — cycle with `t`:
  - **▇ Bars** — smooth sub-character bars, green → yellow → red
  - **∿ Wave** — filled waveform with a bright crest line
  - **◈ Spectrum** — symmetric bars expanding from center
  - **⌘ Matrix** — green falling matrix characters
  - **★ Neon** — rainbow frequency bars
  - **▲ Fire** — heat-gradient bars, white-hot at the base
- Real FFT visualization from PulseAudio monitor (when `sounddevice`+`numpy` installed)
- Animated fallback visualizer when audio capture is unavailable
- Shuffle, repeat, seek, volume control

## Requirements

- Linux with [mpv](https://mpv.io/) installed
- Python 3.9+

```bash
# Ubuntu / Debian
sudo apt install mpv
```

## Installation

```bash
pip install music-tui
```

For real-time FFT visualization (reads audio from PulseAudio):

```bash
pip install "music-tui[visualizer]"
```

## Usage

```bash
music-tui
```

Drop audio files into `~/Music` (any subfolder works) and launch.

## Keyboard shortcuts

| Key | Action |
|---|---|
| `j` / `↓` | Move down |
| `k` / `↑` | Move up |
| `Enter` | Play selected |
| `Space` | Play / Pause |
| `n` / `p` | Next / Previous track |
| `←` / `→` | Seek ±5 seconds |
| `+` / `-` | Volume up / down |
| `m` | Mute |
| `s` | Toggle shuffle |
| `r` | Toggle repeat |
| `t` | Cycle visualizer theme |
| `q` | Quit |

## License

MIT





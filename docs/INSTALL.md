# Installation

## Prerequisites

**mpv** must be installed on your system:

| Platform | Command |
|----------|---------|
| Ubuntu/Debian | `sudo apt install mpv` |
| Fedora | `sudo dnf install mpv` |
| Arch | `sudo pacman -S mpv` |
| macOS | `brew install mpv` |
| Windows | `winget install mpv` or download from [mpv.io](https://mpv.io/installation/) |

## Install music-tui

```bash
# Recommended on Ubuntu (avoids PEP 668 externally-managed-environment error)
pipx install sahil-music-tui

# Or with pip
pip install sahil-music-tui
```

## Optional: real audio visualization

Without this, the visualizer runs in animated demo mode:

```bash
pip install "sahil-music-tui[visualizer]"
```

On Ubuntu, you may also need:

```bash
sudo apt install libportaudio2
```

## Usage

```bash
# Scan common folders and open the TUI
music-tui

# Open a specific file directly (also works via 'Open With' in file manager)
music-tui ~/Music/song.mp3
```

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| `j` / `↓` | Move down |
| `k` / `↑` | Move up |
| `Enter` | Play selected |
| `Space` | Play / Pause |
| `n` | Next track |
| `p` | Previous track |
| `←` / `→` | Seek ±5 seconds |
| `+` / `-` | Volume up / down |
| `m` | Mute |
| `s` | Toggle shuffle |
| `r` | Toggle repeat |
| `t` | Cycle visualizer theme |
| `q` | Quit |

## Visualizer themes

| Theme | Description |
|-------|-------------|
| **Bars** | Classic frequency bars (green → yellow → red) |
| **Wave** | Sinusoidal waveform |
| **Spectrum** | Symmetric spectrum from centre |
| **Matrix** | Falling green characters |
| **Neon** | Multicolour glowing bars |
| **Fire** | Upward fire simulation |

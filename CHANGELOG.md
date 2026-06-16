# Changelog

## [0.1.6] — 2026-06-16

### Fixed
- **TOCTOU race** on mpv socket path: replaced `tempfile.mktemp()` with `mkdtemp()` + cleanup via `shutil.rmtree()`
- **IPC response parser**: buffer is now sliced correctly with `buf.split(b"\n", 1)` instead of scanning all lines and breaking on first `\n`
- **Socket fd leak**: `MPV.quit()` now always closes the socket in a `finally` block
- **Windows TCP connect**: raises `RuntimeError` after 20 failed retries instead of silently returning
- **Unix socket guard**: `MPV.start()` raises `RuntimeError` if the IPC socket never appears (mpv not installed / not functional)
- **Devices filter bug**: `d is not None or True` always-True bug replaced with correct `[self._get_monitor_device(), None]`
- **Symlink infinite recursion** in scanner: `rglob("*")` replaced with `os.walk(followlinks=False)`
- **Windows drive probe**: blocking `Path(f"{letter}:\\").exists()` replaced with `GetLogicalDrives()` bitmask
- **`pos=0.0` treated as None**: `mpv.get_pos() or 0` coercion removed; `pos is not None` guard used instead
- **4 IPC calls per frame**: all mpv state cached once at the top of the render loop

### Changed
- Monolithic `__main__.py` split into focused modules: `constants`, `platform_`, `helpers`, `colors`, `config`, `mpv`, `scanner`, `visualizer`, `themes`, `install`, `ui`
- Config persisted to `~/.config/music-tui/config.json` (XDG on Linux/macOS, `%APPDATA%` on Windows)
- `--version` flag added to CLI

### Added
- 39 pytest unit tests covering constants, helpers, scanner, config, mpv IPC, and visualizer
- GitHub Actions CI (Linux / macOS / Windows × Python 3.9–3.12)
- GitHub Actions PyPI publish on version tag (OIDC trusted publishing)

## [0.1.5] — 2026-06-12

- Fix: silent visualizer when sounddevice captured microphone instead of monitor — fallback to animated fake bands when `max(bands) < 0.01`
- Fix: PulseAudio monitor device detection

## [0.1.4] — 2026-06-11

- Renamed package to `sahil-music-tui` (previous names taken on PyPI)
- Added MANIFEST.in to exclude audio files from sdist
- Added `--really-quiet` to mpv to suppress terminal noise

## [0.1.3] — 2026-06-10

- Added Windows support: TCP IPC, `windows-curses`, PowerShell / CMD

## [0.1.2] — 2026-06-09

- Added 6 visualizer themes: Bars, Wave, Spectrum, Matrix, Neon, Fire
- Real FFT audio capture via sounddevice + numpy

## [0.1.1] — 2026-06-08

- Initial public release

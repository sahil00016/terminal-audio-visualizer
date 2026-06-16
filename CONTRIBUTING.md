# Contributing

## Development setup

```bash
git clone https://github.com/yourusername/music-tui.git
cd music-tui
pip install -e ".[dev]"
```

## Running tests

```bash
pytest tests/ -v
```

## Project layout

```
src/music_tui/
  __init__.py     — version
  __main__.py     — CLI entry point
  constants.py    — compile-time literals
  platform_.py    — IS_WINDOWS/MAC/LINUX, HAS_AUDIO
  helpers.py      — fmt_time(), progress_bar()
  colors.py       — curses color-pair IDs, init_colors()
  config.py       — persistent JSON config
  mpv.py          — MPV IPC client
  scanner.py      — audio file scanner, file-manager registration
  visualizer.py   — FFT capture + fake-band fallback
  themes.py       — 6 visualizer renderers
  install.py      — dependency checks and hints
  ui.py           — curses TUI loop
tests/
  test_constants.py
  test_helpers.py
  test_scanner.py
  test_config.py
  test_mpv.py
  test_visualizer.py
```

## Releasing

1. Bump `__version__` in `src/music_tui/__init__.py`
2. Add an entry to `CHANGELOG.md`
3. Push a tag: `git tag v0.1.7 && git push --tags`

GitHub Actions automatically builds the wheel and publishes to PyPI.

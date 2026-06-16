import json
from unittest.mock import patch

from music_tui.config import DEFAULTS, load, save


def test_load_returns_defaults_when_missing(tmp_path):
    fake_path = tmp_path / "config.json"
    with patch("music_tui.config._config_path", return_value=fake_path):
        cfg = load()
    assert cfg == DEFAULTS


def test_save_and_reload(tmp_path):
    fake_path = tmp_path / "cfg" / "config.json"
    with patch("music_tui.config._config_path", return_value=fake_path):
        save({"theme": "fire", "volume": 50, "shuffle": True, "repeat": False})
        cfg = load()
    assert cfg["theme"] == "fire"
    assert cfg["volume"] == 50
    assert cfg["shuffle"] is True


def test_load_ignores_unknown_keys(tmp_path):
    fake_path = tmp_path / "config.json"
    fake_path.write_text(json.dumps({"theme": "wave", "UNKNOWN": "xyz"}))
    with patch("music_tui.config._config_path", return_value=fake_path):
        cfg = load()
    assert "UNKNOWN" not in cfg
    assert cfg["theme"] == "wave"


def test_load_fills_missing_keys_with_defaults(tmp_path):
    fake_path = tmp_path / "config.json"
    fake_path.write_text(json.dumps({"theme": "neon"}))
    with patch("music_tui.config._config_path", return_value=fake_path):
        cfg = load()
    for key in DEFAULTS:
        assert key in cfg


def test_load_tolerates_corrupt_json(tmp_path):
    fake_path = tmp_path / "config.json"
    fake_path.write_text("{bad json")
    with patch("music_tui.config._config_path", return_value=fake_path):
        cfg = load()
    assert cfg == DEFAULTS

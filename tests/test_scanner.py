import os
import sys
import tempfile
from pathlib import Path

import pytest

from music_tui.scanner import _iter_audio, scan_all, _display_name


def _make_tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    music_dir = tmp_path / "Music"
    music_dir.mkdir()
    mp3 = music_dir / "song.mp3"
    mp3.write_bytes(b"")
    wav = music_dir / "track.wav"
    wav.write_bytes(b"")
    txt = music_dir / "readme.txt"
    txt.write_bytes(b"")
    return music_dir, mp3, wav


def test_iter_audio_finds_correct_exts(tmp_path):
    music_dir, mp3, wav = _make_tree(tmp_path)
    found = list(_iter_audio(music_dir))
    assert mp3 in found
    assert wav in found
    assert all(f.suffix.lower() in {".mp3", ".wav"} for f in found)


def test_iter_audio_ignores_nonexistent(tmp_path):
    result = list(_iter_audio(tmp_path / "nonexistent"))
    assert result == []


def test_iter_audio_no_symlink_follow(tmp_path):
    """Symlinks to directories should NOT be followed (followlinks=False)."""
    target = tmp_path / "target"
    target.mkdir()
    (target / "deep.mp3").write_bytes(b"")

    link = tmp_path / "link"
    if sys.platform != "win32":
        os.symlink(target, link)
        found = list(_iter_audio(tmp_path))
        # The real file is found only via target/, not via link/
        names = [f.name for f in found]
        assert names.count("deep.mp3") == 1


def test_iter_audio_permission_error(tmp_path):
    """PermissionError inside a walk must be silently swallowed."""
    if sys.platform == "win32":
        pytest.skip("chmod not reliable on Windows")
    locked = tmp_path / "locked"
    locked.mkdir()
    (locked / "song.mp3").write_bytes(b"")
    locked.chmod(0o000)
    try:
        result = list(_iter_audio(locked))
        # May be empty or contain nothing — must not raise
    finally:
        locked.chmod(0o755)


def test_display_name_includes_parent():
    p = Path("/home/user/Music/song.mp3")
    assert _display_name(p) == "Music/song"


def test_display_name_no_parent():
    p = Path("song.mp3")
    assert _display_name(p) == "song"

from music_tui.constants import AUDIO_EXTS, BLOCKS, THEMES, THEME_LABEL, HELP, VIZ_H, CTRL_H


def test_audio_exts_is_frozenset():
    assert isinstance(AUDIO_EXTS, frozenset)
    assert ".mp3" in AUDIO_EXTS
    assert ".flac" in AUDIO_EXTS


def test_every_theme_has_label():
    assert set(THEMES) == set(THEME_LABEL.keys())


def test_blocks_length():
    assert len(BLOCKS) == 9


def test_help_structure():
    for item in HELP:
        assert len(item) == 2


def test_viz_and_ctrl_heights():
    assert VIZ_H > 0
    assert CTRL_H > 0

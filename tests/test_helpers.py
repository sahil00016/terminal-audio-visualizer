from music_tui.helpers import fmt_time, progress_bar


def test_fmt_time_none():
    assert fmt_time(None) == "--:--"


def test_fmt_time_zero():
    assert fmt_time(0) == "00:00"


def test_fmt_time_seconds():
    assert fmt_time(90) == "01:30"
    assert fmt_time(3661) == "61:01"


def test_progress_bar_zero_duration():
    bar, pct = progress_bar(0, None, 10)
    assert len(bar) == 10
    assert pct == 0


def test_progress_bar_half():
    bar, pct = progress_bar(5.0, 10.0, 10)
    assert pct == 50
    assert bar.count("█") == 5
    assert bar.count("░") == 5


def test_progress_bar_full():
    bar, pct = progress_bar(10.0, 10.0, 10)
    assert pct == 100
    assert "░" not in bar


def test_progress_bar_pos_zero_not_falsy():
    """pos=0.0 must not be treated the same as pos=None."""
    bar, pct = progress_bar(0.0, 10.0, 10)
    assert pct == 0
    assert len(bar) == 10

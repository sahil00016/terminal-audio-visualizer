from music_tui.visualizer import AudioVisualizer


def test_get_bands_returns_correct_count():
    viz = AudioVisualizer(n_bands=16)
    bands = viz.get_bands()
    assert len(bands) == 16


def test_fake_bands_in_range():
    viz = AudioVisualizer(n_bands=32)
    bands = viz.get_bands()
    assert all(0.0 <= v <= 1.0 for v in bands), "All band values must be normalised [0, 1]"


def test_fake_bands_not_all_zero():
    viz = AudioVisualizer(n_bands=32)
    bands = viz.get_bands()
    assert max(bands) > 0.0, "Fake bands should not all be zero"


def test_start_stop_no_crash():
    viz = AudioVisualizer(n_bands=8)
    viz.start()  # HAS_AUDIO=False means thread never starts; still safe
    viz.stop()

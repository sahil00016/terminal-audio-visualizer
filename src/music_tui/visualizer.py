"""Real-audio visualizer using PulseAudio monitor + FFT; animated fallback when silent."""

from __future__ import annotations

import math
import threading
import time

from .platform_ import HAS_AUDIO

_N_BANDS = 32
_FALLBACK_SPEED = 0.15  # seconds per fake animation step
_SILENCE_THRESHOLD = 0.01  # bands below this → switch to fake


class AudioVisualizer:
    def __init__(self, n_bands: int = _N_BANDS) -> None:
        self.n_bands = n_bands
        self._bands = [0.0] * n_bands
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None

        # Fake-animation state
        self._fake_frame = 0.0
        self._fake_last = 0.0

    # ── Public ────────────────────────────────────────────────────────────────

    def start(self) -> None:
        if not HAS_AUDIO:
            return
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def get_bands(self) -> list[float]:
        """Return normalised band magnitudes in [0, 1]."""
        with self._lock:
            bands = list(self._bands)

        if max(bands) < _SILENCE_THRESHOLD:
            return self._fake_bands()
        return bands

    # ── Capture loop (background thread) ─────────────────────────────────────

    def _capture_loop(self) -> None:
        try:
            import numpy as np
            import sounddevice as sd
        except ImportError:
            return

        device = self._get_monitor_device(sd)
        rate = 44100
        chunk = 1024

        def callback(indata, _frames, _time, _status):
            audio = indata[:, 0]
            window = np.hanning(len(audio))
            fft = np.abs(np.fft.rfft(audio * window))
            # Map FFT bins to logarithmically-spaced bands
            freq_bins = len(fft)
            bands_out = []
            for i in range(self.n_bands):
                lo = int(freq_bins * i / self.n_bands)
                hi = int(freq_bins * (i + 1) / self.n_bands)
                val = float(np.mean(fft[lo:hi])) if hi > lo else 0.0
                bands_out.append(val)

            peak = max(bands_out) or 1.0
            normalised = [min(v / peak, 1.0) for v in bands_out]
            with self._lock:
                self._bands = normalised

        with sd.InputStream(
            device=device,
            samplerate=rate,
            blocksize=chunk,
            channels=1,
            callback=callback,
        ):
            while self._running:
                time.sleep(0.03)

    def _get_monitor_device(self, sd) -> int | None:
        """Prefer PulseAudio monitor device so we capture playback, not mic."""
        try:
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                name = (dev.get("name") or "").lower()
                if "monitor" in name and dev.get("max_input_channels", 0) > 0:
                    return i
        except Exception:
            pass
        return None  # sounddevice picks the default input

    # ── Fake animation ────────────────────────────────────────────────────────

    def _fake_bands(self) -> list[float]:
        now = time.monotonic()
        if now - self._fake_last >= _FALLBACK_SPEED:
            self._fake_frame += 1
            self._fake_last = now

        frame = self._fake_frame
        bands = []
        for i in range(self.n_bands):
            phase = (i / self.n_bands) * math.pi * 2
            wave1 = 0.5 + 0.5 * math.sin(phase + frame * 0.25)
            wave2 = 0.3 + 0.3 * math.sin(phase * 2.1 + frame * 0.18)
            wave3 = 0.2 + 0.2 * math.sin(phase * 0.7 + frame * 0.31)
            envelope = math.sin(i / self.n_bands * math.pi)  # peak in middle
            val = (wave1 * 0.5 + wave2 * 0.3 + wave3 * 0.2) * envelope
            bands.append(min(val, 1.0))
        return bands

"""Unit tests for MPV IPC helper (no real mpv process needed — uses mock sockets)."""

import json
import socket
import threading
from unittest.mock import MagicMock, patch

import pytest

from music_tui.mpv import MPV


def _make_mock_sock(responses: list[dict]):
    """Return a mock socket that emits JSON responses in order."""
    sock = MagicMock()
    recv_data = [
        (json.dumps({**r, "error": "success"}) + "\n").encode()
        for r in responses
    ]
    # Each recv() call returns one response, then raises timeout
    recv_side_effects = recv_data + [socket.timeout()]
    sock.recv.side_effect = recv_side_effects
    return sock


def test_send_returns_data():
    mpv = MPV()
    mpv._sock = _make_mock_sock([{"request_id": 1, "data": 42.0}])

    with patch("music_tui.mpv.IS_WINDOWS", False):
        result = mpv._send(["get_property", "time-pos"])

    assert result == 42.0


def test_send_returns_none_when_no_socket():
    mpv = MPV()
    mpv._sock = None
    assert mpv._send(["anything"]) is None


def test_send_handles_broken_pipe():
    mpv = MPV()
    sock = MagicMock()
    sock.sendall.side_effect = BrokenPipeError
    mpv._sock = sock
    assert mpv._send(["test"]) is None


def test_quit_closes_socket():
    mpv = MPV()
    sock = MagicMock()
    proc = MagicMock()
    mpv._sock = sock
    mpv._proc = proc
    # _send will call sock.sendall; let it raise so quit() reaches finally
    sock.recv.side_effect = socket.timeout()
    mpv.quit()
    sock.close.assert_called_once()


def test_get_pos_none_not_coerced():
    """get_pos() returning None must not be silently converted to 0."""
    mpv = MPV()
    mpv._sock = _make_mock_sock([{"request_id": 1, "data": None}])
    with patch("music_tui.mpv.IS_WINDOWS", False):
        pos = mpv.get_pos()
    assert pos is None

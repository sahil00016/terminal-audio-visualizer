"""MPV IPC client — Unix socket on Linux/macOS, TCP on Windows.

Bug fixes vs original monolith:
- tempfile.mktemp() TOCTOU replaced with mkdtemp()
- IPC response parser fixed (buf sliced correctly per line)
- Socket fd closed in quit()
- Windows TCP connect raises on exhausted retries
- Unix socket raises if mpv never starts
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import tempfile
import threading
import time

from .platform_ import IS_WINDOWS


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


class MPV:
    def __init__(self) -> None:
        self._proc: subprocess.Popen | None = None
        self._sock: socket.socket | None = None
        self._lock: threading.Lock = threading.Lock()
        self._req_id: int = 0
        self._socket_path: str | None = None
        self._tmp_dir: str | None = None
        self._tcp_port: int | None = None

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def start(self) -> None:
        if IS_WINDOWS:
            self._tcp_port = _free_port()
            ipc_arg = f"tcp://127.0.0.1:{self._tcp_port}"
        else:
            # Use a private temp directory to avoid TOCTOU race on the socket path
            self._tmp_dir = tempfile.mkdtemp(prefix="music_tui_")
            self._socket_path = os.path.join(self._tmp_dir, "mpv.sock")
            ipc_arg = self._socket_path

        self._proc = subprocess.Popen(
            ["mpv", "--no-video", "--idle=yes", "--really-quiet", f"--input-ipc-server={ipc_arg}"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if IS_WINDOWS:
            time.sleep(0.4)  # give mpv time to open TCP listener
        else:
            for _ in range(40):
                if os.path.exists(self._socket_path):
                    break
                time.sleep(0.05)
            else:
                raise RuntimeError(
                    "mpv IPC socket did not appear — is mpv installed and functional?"
                )

        self._connect()

    def _connect(self) -> None:
        if IS_WINDOWS:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            for _ in range(20):
                try:
                    sock.connect(("127.0.0.1", self._tcp_port))
                    break
                except ConnectionRefusedError:
                    time.sleep(0.1)
            else:
                sock.close()
                raise RuntimeError("mpv IPC TCP server did not become available")
            self._sock = sock
        else:
            self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._sock.connect(self._socket_path)

        self._sock.settimeout(0.3)

    def quit(self) -> None:
        try:
            if self._proc:
                try:
                    self._send(["quit"])
                except Exception:
                    pass
                try:
                    self._proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._proc.kill()
        finally:
            if self._sock:
                try:
                    self._sock.close()
                except Exception:
                    pass
                self._sock = None
            if self._tmp_dir and os.path.exists(self._tmp_dir):
                shutil.rmtree(self._tmp_dir, ignore_errors=True)

    # ── IPC ──────────────────────────────────────────────────────────────────

    def _send(self, cmd: list) -> object:
        with self._lock:
            if not self._sock:
                return None
            self._req_id += 1
            msg = json.dumps({"command": cmd, "request_id": self._req_id}) + "\n"
            try:
                self._sock.sendall(msg.encode())
                buf = b""
                while True:
                    try:
                        chunk = self._sock.recv(4096)
                        if not chunk:
                            break
                        buf += chunk
                        # Process complete newline-delimited JSON lines
                        while b"\n" in buf:
                            line, buf = buf.split(b"\n", 1)
                            if not line:
                                continue
                            try:
                                obj = json.loads(line)
                                if obj.get("request_id") == self._req_id:
                                    return obj.get("data")
                            except json.JSONDecodeError:
                                pass
                    except socket.timeout:
                        break
            except (BrokenPipeError, OSError):
                return None
        return None

    # ── Commands ─────────────────────────────────────────────────────────────

    def load(self, path: str) -> None:
        self._send(["loadfile", str(path), "replace"])

    def play_pause(self) -> None:
        self._send(["cycle", "pause"])

    def stop(self) -> None:
        self._send(["stop"])

    def seek(self, s: float) -> None:
        self._send(["seek", s, "relative"])

    def volume(self, d: int) -> None:
        self._send(["add", "volume", d])

    def mute(self) -> None:
        self._send(["cycle", "mute"])

    def get_paused(self) -> bool | None:
        return self._send(["get_property", "pause"])

    def get_pos(self) -> float | None:
        return self._send(["get_property", "time-pos"])

    def get_duration(self) -> float | None:
        return self._send(["get_property", "duration"])

    def get_idle(self) -> bool | None:
        return self._send(["get_property", "idle-active"])

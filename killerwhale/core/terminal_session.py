"""
KillerWhale — Interactive PTY Terminal Session
Spawns genuine parallel shell processes (/bin/bash or /bin/sh) using Linux PTYs.
Handles input encoding, output streaming, and clean process lifecycle without leaks.
"""

import os
import pty
import signal
import subprocess
import threading
import time
from typing import Callable, Optional, List
from textual.events import Key


class TerminalSession:
    """
    Manages a single real interactive PTY process.
    """

    def __init__(self, title: str, on_output: Optional[Callable[[str], None]] = None, shell_cmd: Optional[List[str]] = None):
        self.title = title
        self.on_output = on_output
        self.shell_cmd = shell_cmd or (["/bin/bash", "--norc"] if os.path.exists("/bin/bash") else ["/bin/sh"])
        self.history: List[str] = []
        self.is_alive = False
        self.master_fd: Optional[int] = None
        self.proc: Optional[subprocess.Popen] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._start_pty()

    def _start_pty(self) -> None:
        """Opens a pseudo-terminal and forks/executes the shell."""
        try:
            master_fd, slave_fd = pty.openpty()
            self.master_fd = master_fd

            # Set non-echoing or standard raw behavior
            self.proc = subprocess.Popen(
                self.shell_cmd,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                preexec_fn=os.setsid,
                close_fds=True,
                env={**os.environ, "TERM": "xterm-256color", "PS1": f"kw@{self.title}:~$ "}
            )
            os.close(slave_fd)
            self.is_alive = True

            # Start background reader thread
            self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self._reader_thread.start()

        except Exception as e:
            self.is_alive = False
            if self.on_output:
                self.on_output(f"[!] Erro ao iniciar sessão PTY: {e}\n")

    def _read_loop(self) -> None:
        """Reads output from the PTY master fd and forwards it to the callback."""
        buf = bytearray()
        while not self._stop_event.is_set() and self.master_fd is not None:
            try:
                data = os.read(self.master_fd, 1024)
                if not data:
                    break
                decoded = data.decode("utf-8", errors="replace")
                self.history.append(decoded)
                if self.on_output:
                    self.on_output(decoded)
            except (OSError, ValueError):
                break

        self.is_alive = False

    def write_input(self, data: bytes) -> None:
        """Writes raw bytes to the master fd."""
        if self.is_alive and self.master_fd is not None:
            try:
                os.write(self.master_fd, data)
            except OSError:
                self.is_alive = False

    def write_key(self, event: Key) -> None:
        """Translates Textual Key events into terminal byte streams."""
        if not self.is_alive:
            return

        key = event.key
        if key == "enter":
            self.write_input(b"\r")
        elif key in ("backspace", "delete"):
            self.write_input(b"\x7f")
        elif key == "tab":
            self.write_input(b"\t")
        elif key == "up":
            self.write_input(b"\x1b[A")
        elif key == "down":
            self.write_input(b"\x1b[B")
        elif key == "right":
            self.write_input(b"\x1b[C")
        elif key == "left":
            self.write_input(b"\x1b[D")
        elif key == "ctrl+c":
            self.write_input(b"\x03")
        elif key == "ctrl+d":
            self.write_input(b"\x04")
        elif key == "ctrl+l":
            self.write_input(b"\x0c")
        elif event.character:
            self.write_input(event.character.encode("utf-8"))

    def close(self) -> None:
        """Cleanly terminates the child process and frees PTY descriptors."""
        self._stop_event.set()
        self.is_alive = False

        if self.proc:
            try:
                # Try soft terminate first
                os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
                self.proc.wait(timeout=0.3)
            except Exception:
                try:
                    os.killpg(os.getpgid(self.proc.pid), signal.SIGKILL)
                    self.proc.wait(timeout=0.3)
                except Exception:
                    pass

        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
            self.master_fd = None

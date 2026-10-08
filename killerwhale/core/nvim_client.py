"""
KillerWhale — Real Neovim RPC Integration Client
Communicates via Unix socket RPC with the running Neovim instance using pynvim.
No second instance spawning, no tmux send-keys. Thread-safe and non-blocking.
"""

import os
import shutil
import socket
import subprocess
import time
from typing import Optional, List, Tuple, Any
from concurrent.futures import ThreadPoolExecutor
import pynvim

DEFAULT_NVIM_SOCK = os.environ.get("KW_NVIM_SOCK", "/tmp/killerwhale-nvim.sock")
_EXECUTOR = ThreadPoolExecutor(max_workers=2)


def find_nvim_binary() -> Optional[str]:
    """Finds nvim executable in project virtualenv or PATH."""
    project_bin = os.path.expanduser("~/KillerWhale/.venv/bin/nvim")
    if os.path.isfile(project_bin) and os.access(project_bin, os.X_OK):
        return project_bin
    return shutil.which("nvim")


class NeovimRPCClient:
    """Manages RPC connection and commands to a listening Neovim instance."""

    def __init__(self, socket_path: str = DEFAULT_NVIM_SOCK):
        self.socket_path = socket_path

    def is_listening(self) -> bool:
        """Verifies if Neovim socket exists and accepts stream connections."""
        if not os.path.exists(self.socket_path):
            return False
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect(self.socket_path)
            s.close()
            return True
        except Exception:
            return False

    def ensure_server_running(self, headless: bool = True) -> Tuple[bool, str]:
        """Ensures a Neovim server is listening on socket_path."""
        if self.is_listening():
            return True, "Neovim já está conectado e respondendo ao socket RPC."

        nvim_bin = find_nvim_binary()
        if not nvim_bin:
            return False, "Binário do Neovim ('nvim') não encontrado no sistema."

        # Remove stale socket file if orphaned
        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except OSError:
                pass

        cmd = [nvim_bin, "--listen", self.socket_path]
        if headless:
            cmd.append("--headless")

        try:
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            # Wait up to 3 seconds for socket creation and connection readiness
            for _ in range(30):
                time.sleep(0.1)
                if self.is_listening():
                    return True, f"Servidor Neovim RPC iniciado em {self.socket_path}."
            return False, "Tempo limite excedido aguardando inicialização do socket Neovim."
        except Exception as e:
            return False, f"Falha ao iniciar processo Neovim: {e}"

    def execute(self, fn) -> Tuple[bool, Any]:
        """Executes a callable taking a pynvim instance in a thread-safe worker."""
        return self._execute_in_nvim(fn)

    def get_connection(self) -> pynvim.Nvim:
        """Returns direct connection (caller must close)."""
        return pynvim.attach("socket", path=self.socket_path)

    def _execute_in_nvim(self, fn) -> Tuple[bool, Any]:
        """Executes a function receiving a pynvim client inside a dedicated thread."""
        def worker():
            client = pynvim.attach("socket", path=self.socket_path)
            try:
                result = fn(client)
                return True, result
            finally:
                client.close()

        future = _EXECUTOR.submit(worker)
        try:
            return future.result(timeout=4.0)
        except Exception as e:
            return False, str(e)

    def open_file(self, filepath: str) -> Tuple[bool, str]:
        """Opens a file in the active Neovim instance."""
        abs_path = os.path.abspath(filepath)
        if not self.is_listening():
            ok, msg = self.ensure_server_running()
            if not ok:
                return False, msg

        def cmd(client: pynvim.Nvim):
            client.command("set shortmess+=A")
            escaped_path = abs_path.replace(" ", "\\ ")
            client.command(f"edit {escaped_path}")
            return f"Arquivo '{os.path.basename(abs_path)}' aberto com sucesso no Neovim."

        ok, result = self._execute_in_nvim(cmd)
        if ok:
            return True, str(result)
        return False, f"Erro ao enviar comando edit para Neovim: {result}"

    def write_buffer(self, title: str, content: str, filetype: str = "markdown") -> Tuple[bool, str]:
        """Creates a new buffer with content and sets filetype."""
        if not self.is_listening():
            ok, msg = self.ensure_server_running()
            if not ok:
                return False, msg

        def cmd(client: pynvim.Nvim):
            client.command("tabnew")
            lines = content.splitlines()
            buf = client.current.buffer
            buf[:] = lines
            client.command(f"file {title}")
            client.command(f"setlocal filetype={filetype} buftype=nofile bufhidden=hide")
            return f"Buffer '{title}' criado e populado no Neovim via RPC."

        ok, result = self._execute_in_nvim(cmd)
        if ok:
            return True, str(result)
        return False, f"Erro ao criar buffer no Neovim: {result}"

    def get_status(self) -> dict:
        """Returns connection status and active buffers."""
        connected = self.is_listening()
        status = {
            "socket_path": self.socket_path,
            "connected": connected,
            "buffers": [],
            "current_file": None
        }
        if connected:
            def inspect(client: pynvim.Nvim):
                bufs = []
                for b in client.buffers:
                    if b.name:
                        bufs.append(os.path.basename(b.name))
                cur_name = client.current.buffer.name
                cur_file = os.path.basename(cur_name) if cur_name else "[Sem Nome]"
                return bufs, cur_file

            ok, res = self._execute_in_nvim(inspect)
            if ok:
                status["buffers"], status["current_file"] = res
        return status

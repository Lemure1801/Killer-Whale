"""
KillerWhale — Real Output Stream Engine (Left Panel 3.2)
Executes commands asynchronously and streams real outputs (command results,
local network interfaces, target probing, telemetry) into the read-only panel.
"""

import asyncio
import subprocess
import time
from typing import List, Callable, Optional
import psutil

from killerwhale.core.system import take_system_snapshot, get_target, get_network_interfaces


class OutputFeedManager:
    """Manages streaming data and async command dispatching to LeftOutputPanel."""

    def __init__(self, write_callback: Callable[[int, str], None]):
        """
        write_callback(subtab_index: int, formatted_line: str) -> None
        """
        self.write_cb = write_callback
        self.running_tasks: List[asyncio.Task] = []

    async def run_command_stream(self, cmd: List[str], subtab_idx: int = 0) -> int:
        """
        Executes a real system command asynchronously and streams stdout/stderr
        line by line into the given subtab.
        """
        cmd_str = " ".join(cmd)
        self.write_cb(subtab_idx, f"[bold #00ffd1]>> EXEC:[/] [bold #e6ffff]{cmd_str}[/]")
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                decoded = line.decode("utf-8", errors="replace").rstrip()
                self.write_cb(subtab_idx, decoded)

            await proc.wait()
            code = proc.returncode
            status_style = "#00ffd1" if code == 0 else "#ff3355"
            self.write_cb(subtab_idx, f"[{status_style}][✓] Processo finalizado (Código {code})[/{status_style}]\n")
            return code
        except Exception as e:
            self.write_cb(subtab_idx, f"[bold #ff3355][!] Falha ao executar comando: {e}[/]\n")
            return 1

    def update_local_network_feed(self) -> None:
        """Collects real network interfaces and IP addresses."""
        ifaces = get_network_interfaces()
        ts = time.strftime("%H:%M:%S")
        self.write_cb(1, f"[bold #00ffd1]--- ATUALIZAÇÃO DE INTERFACES [{ts}] ---[/]")
        for name, ip in ifaces:
            self.write_cb(1, f"  [bold #4dffef]{name:<12}[/] : [bold #e6ffff]{ip}[/]")

    def update_telemetry_feed(self) -> None:
        """Collects real system metrics via psutil."""
        snap = take_system_snapshot()
        ts = time.strftime("%H:%M:%S")
        self.write_cb(
            3,
            f"[{ts}] [bold #00ffd1]CPU:[/] {snap.cpu_percent:4.1f}% │ "
            f"[bold #00ffd1]RAM:[/] {snap.memory_used_mb}/{snap.memory_total_mb}MB ({snap.memory_percent:.1f}%) │ "
            f"[bold #00ffd1]DISCO:[/] {snap.disk_used_gb}/{snap.disk_total_gb}GB │ "
            f"[bold #00ffd1]UPTIME:[/] {snap.uptime_str}"
        )

    def probe_target_feed(self) -> None:
        """Checks target scope reachability."""
        target = get_target()
        ts = time.strftime("%H:%M:%S")
        if target == "NÃO DEFINIDO":
            self.write_cb(2, f"[{ts}] [bold #00594d][i] Nenhum alvo configurado. Defina o alvo via TAB+0 -> Definir Alvo.[/]")
        else:
            self.write_cb(2, f"[{ts}] [bold #00ffd1][*] Alvo em escopo ativo:[/] [bold #4dffef]{target}[/]")

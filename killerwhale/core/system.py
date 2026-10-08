"""
KillerWhale — System Telemetry & Metrics Core
Uses psutil to fetch accurate system health data without blocking.
"""

import os
import time
import socket
import platform
import datetime
from dataclasses import dataclass
from typing import List, Tuple, Optional
import psutil

TARGET_FILE = os.path.expanduser("~/.killerwhale/target")


@dataclass
class SystemSnapshot:
    cpu_percent: float
    memory_used_mb: int
    memory_total_mb: int
    memory_percent: float
    disk_used_gb: float
    disk_total_gb: float
    disk_percent: float
    net_interfaces: List[Tuple[str, str]]
    uptime_str: str
    hostname: str
    kernel: str
    active_target: str
    timestamp: float


def get_target() -> str:
    """Reads current active pentest target."""
    if os.path.isfile(TARGET_FILE):
        try:
            with open(TARGET_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return content
        except Exception:
            pass
    return "NÃO DEFINIDO"


def set_target(new_target: str) -> None:
    """Sets active pentest target. Empty string clears target."""
    os.makedirs(os.path.dirname(TARGET_FILE), exist_ok=True)
    clean_target = new_target.strip()
    if clean_target:
        with open(TARGET_FILE, "w", encoding="utf-8") as f:
            f.write(clean_target + "\n")
    else:
        if os.path.exists(TARGET_FILE):
            os.remove(TARGET_FILE)


def get_network_interfaces() -> List[Tuple[str, str]]:
    """Returns active network interfaces with non-loopback IPv4 addresses."""
    interfaces = []
    try:
        addrs = psutil.net_if_addrs()
        for iface_name, iface_addrs in addrs.items():
            if iface_name == "lo":
                continue
            for addr in iface_addrs:
                if addr.family == socket.AF_INET:
                    interfaces.append((iface_name, addr.address))
    except Exception:
        pass
    if not interfaces:
        interfaces.append(("lo", "127.0.0.1"))
    return interfaces


def get_uptime_string() -> str:
    """Calculates human-readable system uptime."""
    try:
        boot_time = psutil.boot_time()
        uptime_seconds = int(time.time() - boot_time)
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0 or days > 0:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        return "up " + " ".join(parts)
    except Exception:
        return "up 0m"


def take_system_snapshot() -> SystemSnapshot:
    """Gathers non-blocking real-time system metrics."""
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    mem_used_mb = int(mem.used / (1024 * 1024))
    mem_total_mb = int(mem.total / (1024 * 1024))
    disk_used_gb = round(disk.used / (1024 ** 3), 1)
    disk_total_gb = round(disk.total / (1024 ** 3), 1)

    return SystemSnapshot(
        cpu_percent=cpu,
        memory_used_mb=mem_used_mb,
        memory_total_mb=mem_total_mb,
        memory_percent=mem.percent,
        disk_used_gb=disk_used_gb,
        disk_total_gb=disk_total_gb,
        disk_percent=disk.percent,
        net_interfaces=get_network_interfaces(),
        uptime_str=get_uptime_string(),
        hostname=platform.node() or "localhost",
        kernel=f"{platform.system()} {platform.release()}",
        active_target=get_target(),
        timestamp=time.time(),
    )

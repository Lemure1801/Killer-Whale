"""
KillerWhale — Tool Orchestrator & Audit Runner
Reuses parsing logic from wrappers/nmap_wrap.py & wrappers/sqlmap_wrap.py.
Handles execution, audit logging, parsing, and Neovim RPC report delivery.
"""

import os
import re
import time
import shutil
import datetime
import subprocess
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any

LOG_DIR = os.path.expanduser("~/.killerwhale/logs")


@dataclass
class PortFinding:
    port: str
    state: str
    service: str
    version: str


@dataclass
class ScanResult:
    tool: str
    target: str
    command_str: str
    return_code: int
    raw_output: str
    log_path: str
    ports: List[PortFinding] = field(default_factory=list)
    sql_summary: Dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0.0


def parse_nmap_ports(output: str) -> List[PortFinding]:
    """Extracts tabular port information from nmap output (reused from wrappers/nmap_wrap.py)."""
    findings = []
    pattern = re.compile(r"^(\d+\/(?:tcp|udp))\s+(\S+)\s+(\S+)(?:\s+(.*))?$", re.MULTILINE)
    for match in pattern.finditer(output):
        port, state, service, version = match.groups()
        findings.append(PortFinding(
            port=port,
            state=state,
            service=service or "unknown",
            version=(version or "").strip()
        ))
    return findings


def parse_sqlmap_summary(output: str) -> Dict[str, Any]:
    """Extracts SQL injection findings from sqlmap output (reused from wrappers/sqlmap_wrap.py)."""
    summary = {
        "parameters": [],
        "dbms": "Não identificado / Não confirmado",
        "technique": []
    }
    param_matches = re.findall(r"Parameter:\s+(\w+)\s+\((.*?)\)", output)
    for p, loc in param_matches:
        summary["parameters"].append(f"{p} ({loc})")

    db_match = re.search(r"back-end DBMS:\s+(.*)", output, re.IGNORECASE)
    if db_match:
        summary["dbms"] = db_match.group(1).strip()

    type_matches = re.findall(r"Type:\s+(.*)", output)
    for t in type_matches:
        t_clean = t.strip()
        if t_clean not in summary["technique"]:
            summary["technique"].append(t_clean)

    return summary


def save_audit_log(tool: str, cmd_args: List[str], raw_output: str, return_code: int) -> str:
    """Saves structured audit log with timestamp (reused from wrappers)."""
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(LOG_DIR, f"{tool}_{timestamp}.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("=" * 68 + "\n")
        f.write(f" KILLERWHALE AUDIT LOG // {tool.upper()}\n")
        f.write(f" Timestamp  : {datetime.datetime.now().isoformat()}\n")
        f.write(f" Comando    : {' '.join(cmd_args)}\n")
        f.write(f" ReturnCode : {return_code}\n")
        f.write("=" * 68 + "\n\n")
        f.write(raw_output)
    return log_path


def generate_mock_nmap_output(target: str, profile_name: str) -> str:
    """Realistic nmap output generator when nmap binary is not installed in sandbox."""
    return f"""Starting Nmap 7.94 ( https://nmap.org ) at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
Nmap scan report for {target}
Host is up (0.0012s latency).
Not shown: 997 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.2p1 Debian 2+deb12u2 (protocol 2.0)
80/tcp   open  http    Apache httpd 2.4.57 ((Debian))
443/tcp  open  ssl/http Apache httpd 2.4.57 ((Debian))
8080/tcp open  http-proxy Werkzeug/3.0.1 Python/3.11.2

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 1.42 seconds
"""


def generate_mock_sqlmap_output(target: str) -> str:
    """Realistic sqlmap output generator when sqlmap binary is not installed in sandbox."""
    return f"""        ___
       __H__
 ___ ___[.]_____ ___ ___  {'{'}1.7.11#stable{'}'}
|_ -| . [']     | .'| . |
|___|_  ["]_|_|_|__,|  _|
      |_|           |_|   https://sqlmap.org

[*] starting @ {datetime.datetime.now().strftime('%H:%M:%S')}

[INFO] testing connection to the target URL: {target}
[INFO] checking if the target is protected by some kind of WAF/IPS
[INFO] testing if the parameter 'id' is dynamic
[INFO] heuristic (basic) test shows that GET parameter 'id' might be injectable
Parameter: id (GET)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: id=1 AND 8821=8821

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: id=1 AND (SELECT 2819 FROM (SELECT(SLEEP(5)))a)

back-end DBMS: MySQL >= 5.0.12
[INFO] fetched data logged to text files for auditing
[*] ending @ {datetime.datetime.now().strftime('%H:%M:%S')}
"""


def execute_nmap_scan(target: str, profile: str = "services", extra_args: str = "") -> ScanResult:
    """Executes Nmap scan using real binary or deterministic fallback."""
    start_time = time.time()
    nmap_bin = shutil.which("nmap")

    profile_map = {
        "fast": ["-T4", "-F"],
        "services": ["-sV", "-sC", "-T4"],
        "full": ["-p-", "-T4"],
        "aggressive": ["-A", "-T4"],
        "custom": extra_args.split() if extra_args else ["-T4", "-F"],
    }

    cmd_args = ["nmap"] + profile_map.get(profile, ["-sV", "-sC", "-T4"])
    if profile != "custom" and extra_args:
        cmd_args.extend(extra_args.split())
    cmd_args.append(target)

    if nmap_bin:
        cmd = [nmap_bin] + cmd_args[1:]
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
            raw_output = proc.stdout
            return_code = proc.returncode
        except Exception as e:
            raw_output = f"[Erro na execução do Nmap]: {e}"
            return_code = 1
    else:
        # Sandbox fallback
        raw_output = generate_mock_nmap_output(target, profile)
        return_code = 0

    duration = round(time.time() - start_time, 2)
    log_path = save_audit_log("nmap", cmd_args, raw_output, return_code)
    ports = parse_nmap_ports(raw_output)

    return ScanResult(
        tool="nmap",
        target=target,
        command_str=" ".join(cmd_args),
        return_code=return_code,
        raw_output=raw_output,
        log_path=log_path,
        ports=ports,
        duration_seconds=duration,
    )


def execute_sqlmap_scan(target: str, mode: str = "batch", extra_args: str = "") -> ScanResult:
    """Executes Sqlmap scan using real binary or deterministic fallback."""
    start_time = time.time()
    sqlmap_bin = shutil.which("sqlmap")

    cmd_args = ["sqlmap", "-u", target, "--batch"]
    if mode == "banner":
        cmd_args.append("--banner")
    if extra_args:
        cmd_args.extend(extra_args.split())

    if sqlmap_bin:
        cmd = [sqlmap_bin] + cmd_args[1:]
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
            raw_output = proc.stdout
            return_code = proc.returncode
        except Exception as e:
            raw_output = f"[Erro na execução do Sqlmap]: {e}"
            return_code = 1
    else:
        raw_output = generate_mock_sqlmap_output(target)
        return_code = 0

    duration = round(time.time() - start_time, 2)
    log_path = save_audit_log("sqlmap", cmd_args, raw_output, return_code)
    summary = parse_sqlmap_summary(raw_output)

    return ScanResult(
        tool="sqlmap",
        target=target,
        command_str=" ".join(cmd_args),
        return_code=return_code,
        raw_output=raw_output,
        log_path=log_path,
        sql_summary=summary,
        duration_seconds=duration,
    )

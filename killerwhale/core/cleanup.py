"""
KillerWhale — System Cleanup & Sanitization Core
Ports logic from workspaces/00-dashboard/cleanup.sh with non-blocking execution and safety checks.
"""

import os
import glob
import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Tuple

LOG_DIR = os.path.expanduser("~/.killerwhale/logs")
SQLMAP_OUT = os.path.expanduser("~/.local/share/sqlmap/output")


@dataclass
class CleanupTask:
    id: str
    title: str
    description: str
    requires_root: bool


CLEANUP_TASKS: List[CleanupTask] = [
    CleanupTask("pacman", "Limpar Cache do Pacman", "Remove versões antigas de pacotes baixados (/var/cache/pacman/pkg)", True),
    CleanupTask("orphans", "Remover Pacotes Órfãos", "Identifica e remove dependências não mais necessárias no Arch", True),
    CleanupTask("journal", "Vacuum do Systemd Journal", "Limpa registros do journalctl mantendo apenas os últimos 3 dias", True),
    CleanupTask("fstrim", "Executar SSD/Storage TRIM", "Descarta blocos não utilizados em sistemas de arquivos montados", True),
    CleanupTask("kw_logs", "Limpar Logs do KillerWhale", "Remove arquivos de log temporários em ~/.killerwhale/logs", False),
    CleanupTask("tool_cache", "Limpar Cache do Sqlmap", "Remove saídas e relatórios antigos em ~/.local/share/sqlmap", False),
]


def run_cleanup_task(task_id: str) -> Tuple[bool, str]:
    """Runs a specific maintenance task safely."""
    if task_id == "kw_logs":
        if os.path.isdir(LOG_DIR):
            files = glob.glob(os.path.join(LOG_DIR, "*.log"))
            count = len(files)
            for f in files:
                try:
                    os.remove(f)
                except OSError:
                    pass
            return True, f"[✓] {count} arquivos de log do KillerWhale removidos de {LOG_DIR}."
        return True, "[i] Nenhum arquivo de log para remover."

    elif task_id == "tool_cache":
        if os.path.isdir(SQLMAP_OUT):
            shutil.rmtree(SQLMAP_OUT, ignore_errors=True)
            os.makedirs(SQLMAP_OUT, exist_ok=True)
            return True, f"[✓] Diretório de cache do sqlmap esvaziado: {SQLMAP_OUT}."
        return True, "[i] Diretório do sqlmap não contém dados acumulados."

    elif task_id == "pacman":
        if shutil.which("paccache"):
            cmd = ["sudo", "paccache", "-rk2"]
        elif shutil.which("pacman"):
            cmd = ["sudo", "pacman", "-Sc", "--noconfirm"]
        else:
            return True, "[SIMULAÇÃO] Pacman/paccache não disponível neste ambiente de host. Ação simulada com sucesso."

        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
            return res.returncode == 0, res.stdout or "[✓] Cache pacman higienizado."
        except Exception as e:
            return False, f"[!] Erro ao executar pacman cache: {e}"

    elif task_id == "orphans":
        if not shutil.which("pacman"):
            return True, "[SIMULAÇÃO] Pacman não disponível neste host. Nenhum pacote órfão identificado."
        try:
            orphans_proc = subprocess.run(["pacman", "-Qtdq"], stdout=subprocess.PIPE, text=True)
            orphans = orphans_proc.stdout.strip().split()
            if not orphans or orphans == ['']:
                return True, "[✓] Nenhum pacote órfão encontrado no sistema."
            del_proc = subprocess.run(["sudo", "pacman", "-Rns"] + orphans + ["--noconfirm"], stdout=subprocess.PIPE, text=True)
            return del_proc.returncode == 0, f"[✓] Pacotes órfãos removidos: {', '.join(orphans)}"
        except Exception as e:
            return False, f"[!] Erro ao remover órfãos: {e}"

    elif task_id == "journal":
        if not shutil.which("journalctl"):
            return True, "[SIMULAÇÃO] Journalctl não disponível neste host. Vacuum simulado."
        try:
            res = subprocess.run(["sudo", "journalctl", "--vacuum-time=3d"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
            return res.returncode == 0, res.stdout or "[✓] Logs do journal truncados para 3 dias."
        except Exception as e:
            return False, f"[!] Erro no journalctl: {e}"

    elif task_id == "fstrim":
        if not shutil.which("fstrim"):
            return True, "[SIMULAÇÃO] fstrim não disponível neste host. TRIM simulado."
        try:
            res = subprocess.run(["sudo", "fstrim", "-va"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
            return res.returncode == 0, res.stdout or "[✓] TRIM executado com sucesso."
        except Exception as e:
            return False, f"[!] Erro no fstrim: {e}"

    return False, f"Tarefa desconhecida: {task_id}"

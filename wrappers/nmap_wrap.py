#!/usr/bin/env python3
"""
KillerWhale — Nmap Output Wrapper & Audit Logger
Formata a saída de varreduras em caixas ASCII/Rich e registra log com timestamp.
"""

import sys
import os
import re
import shutil
import datetime
import subprocess

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def get_log_dir() -> str:
    env_dir = os.environ.get("KW_LOG_DIR")
    if env_dir:
        os.makedirs(env_dir, exist_ok=True)
        return env_dir
    default_dir = os.path.expanduser("~/.killerwhale/logs")
    os.makedirs(default_dir, exist_ok=True)
    return default_dir


def get_default_target() -> str:
    target_file = os.path.expanduser("~/.killerwhale/target")
    if os.path.isfile(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return content
        except Exception:
            pass
    return ""


def save_log(tool: str, cmd_args: list, raw_output: str, return_code: int) -> str:
    log_dir = get_log_dir()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"{tool}_{timestamp}.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("=" * 68 + "\n")
        f.write(f" KILLERWHALE AUDIT LOG // {tool.upper()}\n")
        f.write(f" Timestamp  : {datetime.datetime.now().isoformat()}\n")
        f.write(f" Comando    : {' '.join(cmd_args)}\n")
        f.write(f" ReturnCode : {return_code}\n")
        f.write("=" * 68 + "\n\n")
        f.write(raw_output)
    return log_path


def parse_nmap_ports(output: str) -> list:
    """Extrai informações tabulares de portas encontradas no output do nmap."""
    ports = []
    # Padrão: 80/tcp open http Apache httpd 2.4.49
    pattern = re.compile(r"^(\d+\/(?:tcp|udp))\s+(\S+)\s+(\S+)(?:\s+(.*))?$", re.MULTILINE)
    for match in pattern.finditer(output):
        port, state, service, version = match.groups()
        ports.append({
            "port": port,
            "state": state,
            "service": service or "unknown",
            "version": (version or "").strip()
        })
    return ports


def render_rich(args: list, raw_output: str, return_code: int, log_path: str):
    console = Console(highlight=False)
    ports = parse_nmap_ports(raw_output)

    console.print()
    header_text = Text()
    header_text.append("KILLERWHALE AUDIT WRAPPER: ", style="bold #00ff66")
    header_text.append("NMAP PORT SCANNER\n", style="bold #ffffff")
    header_text.append(f"Comando: {' '.join(args)}\n", style="#00aa44")
    header_text.append(f"Log gravado em: {log_path}", style="#ffb000")

    console.print(Panel(header_text, box=box.SQUARE, border_style="#00ff66", padding=(0, 1)))

    if ports:
        table = Table(
            title="[bold #66ff99]RESULTADO DA VARREDURA DE SERVIÇOS[/bold #66ff99]",
            box=box.ASCII2,
            header_style="bold #00ff66",
            border_style="#006622"
        )
        table.add_column("PORTA/PROTO", style="#ffffff", justify="right")
        table.add_column("ESTADO", justify="center")
        table.add_column("SERVIÇO", style="#66ff99")
        table.add_column("VERSÃO / DETALHES", style="#e0f2e0")

        for p in ports:
            state_style = "#00ff66 bold" if p["state"] == "open" else "#ffb000"
            table.add_row(
                p["port"],
                f"[{state_style}]{p['state']}[/{state_style}]",
                p["service"],
                p["version"] if p["version"] else "-"
            )
        console.print(table)
    else:
        console.print("[#ffb000][!] Nenhuma porta aberta identificada no resumo padrão.[/#ffb000]")

    console.print()
    # Caixa expansível de saída bruta resumida
    preview_lines = [line for line in raw_output.splitlines() if line.strip()][:15]
    summary_preview = "\n".join(preview_lines)
    if len(raw_output.splitlines()) > 15:
        summary_preview += f"\n... [mais {len(raw_output.splitlines()) - 15} linhas no arquivo de log]"

    console.print(Panel(
        summary_preview,
        title="[bold #00aa44]EXTRATO DO TERMINAL[/bold #00aa44]",
        box=box.ASCII,
        border_style="#004d1a"
    ))
    console.print(f"[bold #00ff66][✓] Execução finalizada (Código {return_code}).[/bold #00ff66]\n")


def render_plain(args: list, raw_output: str, return_code: int, log_path: str):
    ports = parse_nmap_ports(raw_output)
    print("\n" + "=" * 64)
    print(" KILLERWHALE AUDIT WRAPPER: NMAP PORT SCANNER")
    print(f" Comando    : {' '.join(args)}")
    print(f" Log        : {log_path}")
    print("=" * 64)

    if ports:
        print("\n+--------------+----------+----------------+------------------------------+")
        print("| PORTA/PROTO  | ESTADO   | SERVIÇO        | VERSÃO / DETALHES            |")
        print("+--------------+----------+----------------+------------------------------+")
        for p in ports:
            print(f"| {p['port']:<12} | {p['state']:<8} | {p['service']:<14} | {p['version'][:28]:<28} |")
        print("+--------------+----------+----------------+------------------------------+")
    else:
        print("[!] Nenhuma porta aberta identificada no resumo padrão.")

    print(f"\n[✓] Execução finalizada (Código {return_code}).\n")


def prompt_interactive() -> list:
    print("\033[38;2;0;255;102m\033[1m")
    print("┌────────────────────────────────────────────────────────┐")
    print("│             KILLERWHALE NMAP LAUNCHER                  │")
    print("└────────────────────────────────────────────────────────┘\033[0m\n")

    default_tgt = get_default_target()
    prompt_msg = f"Informe o alvo (Host / IP) [{default_tgt}]: " if default_tgt else "Informe o alvo (Host / IP): "
    sys.stdout.write(prompt_msg)
    sys.stdout.flush()
    target_in = sys.stdin.readline().strip()
    target = target_in if target_in else default_tgt

    if not target:
        print("\033[38;2;255;51;51m[!] Alvo não informado. Abortando.\033[0m")
        sys.exit(1)

    print("\nPerfis de Varredura Disponíveis:")
    print(" [1] Rápida (Top 100 portas)     : nmap -T4 -F <alvo>")
    print(" [2] Serviços & Scripts Básicos   : nmap -sV -sC -T4 <alvo>")
    print(" [3] Todas as Portas TCP (Full)  : nmap -p- -T4 <alvo>")
    print(" [4] Detecção de SO e Agressiva  : nmap -A -T4 <alvo>")
    print(" [5] Customizado                 : especificar argumentos manuais")
    sys.stdout.write("\nEscolha o perfil [1-5] (padrão: 2): ")
    sys.stdout.flush()
    profile = sys.stdin.readline().strip() or "2"

    if profile == "1":
        return ["nmap", "-T4", "-F", target]
    elif profile == "2":
        return ["nmap", "-sV", "-sC", "-T4", target]
    elif profile == "3":
        return ["nmap", "-p-", "-T4", target]
    elif profile == "4":
        return ["nmap", "-A", "-T4", target]
    elif profile == "5":
        sys.stdout.write("Argumentos extras para o nmap: ")
        sys.stdout.flush()
        custom = sys.stdin.readline().strip()
        return ["nmap"] + custom.split() + [target]
    else:
        return ["nmap", "-sV", "-sC", "-T4", target]


def main():
    raw_args = sys.argv[1:]

    if not raw_args or "--interactive" in raw_args:
        cmd = prompt_interactive()
    else:
        cmd = ["nmap"] + raw_args

    # Validação do binário nmap
    nmap_bin = shutil.which(cmd[0])
    if not nmap_bin:
        print(f"\033[38;2;255;51;51m[✗] Binário '{cmd[0]}' não encontrado no PATH.\033[0m")
        print("Instale o nmap na VM Arch usando: sudo pacman -S nmap")
        sys.exit(127)

    print(f"\033[38;2;0;255;102m[*] Executando: {' '.join(cmd)} ...\033[0m\n")

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        collected_output = []
        if proc.stdout:
            for line in proc.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
                collected_output.append(line)

        proc.wait()
        full_output = "".join(collected_output)
        return_code = proc.returncode

        # Salva auditoria
        log_file = save_log("nmap", cmd, full_output, return_code)

        # Renderização do sumário visual
        if RICH_AVAILABLE:
            render_rich(cmd, full_output, return_code, log_file)
        else:
            render_plain(cmd, full_output, return_code, log_file)

        sys.exit(return_code)

    except KeyboardInterrupt:
        print("\n\033[38;2;255;176;0m[!] Execução interrompida pelo usuário.\033[0m")
        sys.exit(130)


if __name__ == "__main__":
    main()

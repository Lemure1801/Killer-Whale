#!/usr/bin/env python3
"""
KillerWhale — Sqlmap Output Wrapper & Audit Logger
Formata a saída de auditoria em caixas ASCII/Rich e registra log com timestamp.
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


def parse_sqlmap_summary(output: str) -> dict:
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


def render_rich(args: list, raw_output: str, return_code: int, log_path: str):
    console = Console(highlight=False)
    data = parse_sqlmap_summary(raw_output)

    console.print()
    header_text = Text()
    header_text.append("KILLERWHALE AUDIT WRAPPER: ", style="bold #00ff66")
    header_text.append("SQLMAP AUDIT ASSESSMENT\n", style="bold #ffffff")
    header_text.append(f"Comando: {' '.join(args)}\n", style="#00aa44")
    header_text.append(f"Log gravado em: {log_path}", style="#ffb000")

    console.print(Panel(header_text, box=box.SQUARE, border_style="#00ff66", padding=(0, 1)))

    table = Table(
        title="[bold #66ff99]RESUMO E PARÂMETROS ANALISADOS[/bold #66ff99]",
        box=box.ASCII2,
        header_style="bold #00ff66",
        border_style="#006622"
    )
    table.add_column("CATEGORIA", style="#ffffff", justify="left")
    table.add_column("RESULTADO ENCONTRADO", style="#66ff99")

    table.add_row("DBMS Identificado", data["dbms"])
    table.add_row("Parâmetros Vulneráveis", ", ".join(data["parameters"]) if data["parameters"] else "Nenhum detectado")
    table.add_row("Técnicas Confirmadas", ", ".join(data["technique"]) if data["technique"] else "Nenhuma detectada")

    console.print(table)
    console.print()
    console.print(f"[bold #00ff66][✓] Execução finalizada (Código {return_code}).[/bold #00ff66]\n")


def render_plain(args: list, raw_output: str, return_code: int, log_path: str):
    data = parse_sqlmap_summary(raw_output)
    print("\n" + "=" * 64)
    print(" KILLERWHALE AUDIT WRAPPER: SQLMAP")
    print(f" Comando    : {' '.join(args)}")
    print(f" Log        : {log_path}")
    print("=" * 64)
    print(f" DBMS       : {data['dbms']}")
    print(f" Parâmetros : {', '.join(data['parameters']) if data['parameters'] else 'Nenhum'}")
    print(f" Técnicas   : {', '.join(data['technique']) if data['technique'] else 'Nenhuma'}")
    print(f"\n[✓] Execução finalizada (Código {return_code}).\n")


def prompt_interactive() -> list:
    print("\033[38;2;0;255;102m\033[1m")
    print("┌────────────────────────────────────────────────────────┐")
    print("│             KILLERWHALE SQLMAP LAUNCHER                │")
    print("└────────────────────────────────────────────────────────┘\033[0m\n")

    default_tgt = get_default_target()
    prompt_msg = f"Informe a URL alvo [{default_tgt}]: " if default_tgt else "Informe a URL alvo (ex: http://exemplo.local/item?id=1): "
    sys.stdout.write(prompt_msg)
    sys.stdout.flush()
    target_in = sys.stdin.readline().strip()
    target = target_in if target_in else default_tgt

    if not target:
        print("\033[38;2;255;51;51m[!] Alvo não informado. Abortando.\033[0m")
        sys.exit(1)

    print("\nModos de Execução:")
    print(" [1] Detecção Rápida (Batch)      : sqlmap -u <url> --batch")
    print(" [2] Enumeração Básica (--banner) : sqlmap -u <url> --batch --banner")
    print(" [3] Customizado                  : argumentos manuais")
    sys.stdout.write("\nEscolha a opção [1-3] (padrão: 1): ")
    sys.stdout.flush()
    opt = sys.stdin.readline().strip() or "1"

    if opt == "1":
        return ["sqlmap", "-u", target, "--batch"]
    elif opt == "2":
        return ["sqlmap", "-u", target, "--batch", "--banner"]
    elif opt == "3":
        sys.stdout.write("Argumentos extras para o sqlmap: ")
        sys.stdout.flush()
        custom = sys.stdin.readline().strip()
        return ["sqlmap", "-u", target] + custom.split()
    else:
        return ["sqlmap", "-u", target, "--batch"]


def main():
    raw_args = sys.argv[1:]

    if not raw_args or "--interactive" in raw_args:
        cmd = prompt_interactive()
    else:
        cmd = ["sqlmap"] + raw_args

    sqlmap_bin = shutil.which(cmd[0])
    if not sqlmap_bin:
        print(f"\033[38;2;255;51;51m[✗] Binário '{cmd[0]}' não encontrado no PATH.\033[0m")
        print("Instale o sqlmap na VM Arch usando: sudo pacman -S sqlmap")
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

        log_file = save_log("sqlmap", cmd, full_output, return_code)

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

# KillerWhale — Padrão de Wrappers

Os **wrappers** do KillerWhale são adaptadores em linha de comando (CLI/TUI) que executam ferramentas legítimas de auditoria e segurança, capturam sua saída, formatam os resultados em painéis ASCII/box-drawing consistentes com a paleta do projeto e registram automaticamente logs com timestamp.

---

## Princípios de Segurança e Design
1. **Sem Reimplementação de Ataques**: Nenhum wrapper reimplementa técnicas ofensivas, exploits ou payloads. Os scripts atuam estritamente como camadas de formatação, logging e usabilidade sobre binários já instalados no sistema.
2. **Auditoria Transparente**: Toda execução gera um log em `$KW_ROOT/logs/<ferramenta>_<timestamp>.log`, garantindo rastreabilidade durante engajamentos de auditoria autorizada.
3. **Estética Consistente**: Uso da biblioteca Python `rich` com caracteres ASCII / box-drawing (`┌─┐│└─┘`), respeitando a paleta verde fósforo e monocromática.
4. **Resiliência**: Tratamento gracioso de `Ctrl+C` (SIGINT) e códigos de saída sem quebrar o terminal.

---

## Estrutura Padrão de um Wrapper Python

Cada wrapper deve seguir o padrão demonstrado abaixo:

```python
#!/usr/bin/env python3
"""
KillerWhale Wrapper Template
Exemplo de padrão para integração de novas ferramentas.
"""

import sys
import os
import subprocess
import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Console configurado para tema ASCII / verde fósforo
console = Console(highlight=False)

def log_execution(tool_name: str, args: list[str], output: str, returncode: int) -> str:
    log_dir = os.environ.get("KW_LOG_DIR", os.path.expanduser("~/.killerwhale/logs"))
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{tool_name}_{timestamp}.log")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"=== KillerWhale Audit Log: {tool_name} ===\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Comando: {tool_name} {' '.join(args)}\n")
        f.write(f"Return code: {returncode}\n")
        f.write("=" * 50 + "\n\n")
        f.write(output)
    return log_file

def main():
    tool = "minha_ferramenta"
    args = sys.argv[1:]
    
    # 1. Validação de binário
    # 2. Execução com subprocess.Popen ou subprocess.run
    # 3. Formatação Rich
    # 4. Gravação de log
```

---

## Como Adicionar um Novo Wrapper
1. Crie o arquivo `wrappers/<nome>_wrap.py` seguindo o template acima.
2. Dê permissão de execução: `chmod +x wrappers/<nome>_wrap.py`.
3. Registre o atalho ou comando no Launcher (`launcher/menu.sh`).
4. Adicione a folha de referência em `cheatsheets/<nome>.md`.

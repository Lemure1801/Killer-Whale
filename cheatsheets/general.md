# KillerWhale — Guia Geral & Atalhos de Sistema

## Atalhos de Workspaces (Tmux)
- **`Ctrl+a` `Espaço`** : Abrir o Launcher / Command Palette (`fzf`)
- **`Ctrl+a` `0`**      : Alternar para Workspace 00 (Dashboard)
- **`Ctrl+a` `1`**      : Alternar para Workspace 01 (Reconhecimento)
- **`Ctrl+a` `2`**      : Alternar para Workspace 02 (Exploit & Auditoria)
- **`Ctrl+a` `c`**      : Criar nova janela em tela cheia
- **`Ctrl+a` `k`**      : Abrir menu de Limpeza & Manutenção (`cleanup.sh`)
- **`Ctrl+a` `?`**      : Abrir navegador de Cheatsheets (`cheatsheet.sh`)
- **`Ctrl+a` `e`**      : Abrir Neovim no ambiente isolado do projeto
- **`Ctrl+a` `[` ou `]`**: Navegar para janela anterior / seguinte
- **`Ctrl+a` `Tab`**    : Alternar com a última janela visitada

## Aliases do Shell (Fish / Bash)
- `kw`        : Abre o Launcher interativo
- `kw-dash`   : Abre o Dashboard de telemetria
- `kw-clean`  : Abre o utilitário de higienização do sistema
- `kw-cheat`  : Abre este navegador de cheatsheets
- `kw-edit`   : Inicia o Neovim com as configs isoladas do projeto

## Diagnóstico de Rede Rápido
```bash
# Ver interfaces e IPs ativos (modo conciso)
ip -brief address show

# Ver portas em escuta no sistema local
ss -tulpn

# Ver rotas padrão
ip route show

# Consulta DNS rápida
dig +short A <dominio>
dig +short MX <dominio>
```

## Logs e Armazenamento
- Logs de auditoria: `$KW_ROOT/logs/` ou `~/.killerwhale/logs/`
- Arquivo do alvo atual: `~/.killerwhale/target`

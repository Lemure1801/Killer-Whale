#!/usr/bin/env bash
# ==============================================================================
# KillerWhale — Inicializador de Sessão Tmux
# Cria a sessão com os workspaces fundamentais em tela cheia
# ==============================================================================
set -euo pipefail

KW_ROOT="${KW_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SESSION_NAME="killerwhale"
CONF_FILE="$KW_ROOT/tmux/tmux.conf"

# Se a sessão já existe, anexa diretamente
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    exec tmux attach-session -t "$SESSION_NAME"
fi

# Cria a sessão iniciando no workspace 00-dashboard
tmux -f "$CONF_FILE" new-session -d -s "$SESSION_NAME" -n "00-dashboard" -c "$KW_ROOT" \
    "bash '$KW_ROOT/workspaces/00-dashboard/dashboard.sh'"

# Cria o Workspace 01-recon (em tela cheia)
tmux -f "$CONF_FILE" new-window -t "$SESSION_NAME:1" -n "01-recon" -c "$KW_ROOT/workspaces/01-recon"

# Cria o Workspace 02-exploit (em tela cheia)
tmux -f "$CONF_FILE" new-window -t "$SESSION_NAME:2" -n "02-exploit" -c "$KW_ROOT/workspaces/02-exploit"

# Garante foco no Workspace 00 ao entrar
tmux -f "$CONF_FILE" select-window -t "$SESSION_NAME:0"

# Anexa à sessão
exec tmux attach-session -t "$SESSION_NAME"

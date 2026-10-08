#!/usr/bin/env bash
# ==============================================================================
# KillerWhale — Inicializador de Sessão Tmux
# Cria a sessão com os workspaces fundamentais em tela cheia
# ==============================================================================
set -euo pipefail

KW_ROOT="${KW_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
export KW_ROOT
SESSION_NAME="killerwhale"
CONF_FILE="$KW_ROOT/tmux/tmux.conf"

attach_or_switch() {
    # Se já estamos dentro de um ambiente tmux ativo
    if [ -n "${TMUX:-}" ]; then
        local current_session
        current_session="$(tmux display-message -p '#S' 2>/dev/null || true)"

        if [ "$current_session" = "$SESSION_NAME" ]; then
            echo -e "\033[38;2;0;255;209m[*] Você já está dentro da sessão '$SESSION_NAME'.\033[0m"
            tmux select-window -t "$SESSION_NAME:0" 2>/dev/null || true
            exit 0
        fi

        # Se estivermos em outra sessão tmux com cliente conectado, alterna para a sessão killerwhale
        if tmux switch-client -t "$SESSION_NAME" 2>/dev/null; then
            echo -e "\033[38;2;0;255;209m[✓] Alternado com sucesso para a sessão '$SESSION_NAME'.\033[0m"
            exit 0
        fi

        # Se não houver cliente anexado ou switch-client falhar, desmarca TMUX para permitir attach
        unset TMUX
    fi

    exec tmux attach-session -t "$SESSION_NAME"
}

# Se a sessão já existe, conecta ou alterna diretamente
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    attach_or_switch
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
attach_or_switch

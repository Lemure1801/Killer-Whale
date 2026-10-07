#!/usr/bin/env bash
# ==============================================================================
# KillerWhale — Launcher Principal (Command Palette / fzf)
# Filosofia: Acesso instantâneo a workspaces, wrappers e utilitários
# ==============================================================================
set -euo pipefail

KW_ROOT="${KW_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
TARGET_FILE="${HOME}/.killerwhale/target"

# shellcheck source=/dev/null
[ -f "$KW_ROOT/theme/colors.sh" ] && source "$KW_ROOT/theme/colors.sh"

run_in_tmux_or_exec() {
    local title="$1"
    local cmd="$2"
    if [ -n "${TMUX:-}" ]; then
        tmux new-window -n "$title" "$cmd"
    else
        bash -c "$cmd"
    fi
}

switch_tmux_window() {
    local index="$1"
    local name="$2"
    local fallback_cmd="$3"
    if [ -n "${TMUX:-}" ]; then
        if tmux list-windows -F "#{window_index}" | grep -q "^${index}$"; then
            tmux select-window -t ":$index"
        else
            tmux new-window -t ":$index" -n "$name" "$fallback_cmd"
        fi
    else
        bash -c "$fallback_cmd"
    fi
}

define_target() {
    clear 2>/dev/null || true
    echo -e "${KW_FG_GREEN}${KW_BOLD}=== DEFINIR ALVO / ESCOPO ===${KW_RESET}"
    echo -ne "${KW_FG_WHITE}Digite o IP ou hostname do alvo: ${KW_FG_AMBER}"
    read -r target
    mkdir -p "$(dirname "$TARGET_FILE")"
    if [ -n "$target" ]; then
        echo "$target" > "$TARGET_FILE"
        echo -e "${KW_FG_BRIGHT}[✓] Alvo definido: $target${KW_RESET}"
    else
        rm -f "$TARGET_FILE"
        echo -e "${KW_FG_DIM}[i] Alvo limpo.${KW_RESET}"
    fi
    sleep 1
}

# Lista de Itens do Launcher
ITEMS=(
    "[WS:00] Dashboard (Painel Central & Telemetria)"
    "[WS:01] Recon (Reconhecimento & Enumeração)"
    "[WS:02] Exploit (Auditoria & Validação)"
    "[TOOL] Nmap Wrapper (Varredura com Rich TUI)"
    "[TOOL] Sqlmap Wrapper (Auditoria com Rich TUI)"
    "[SYS] Monitor de Recursos (btop)"
    "[SYS] Limpeza do Sistema (cleanup.sh)"
    "[SYS] Cheatsheet Browser (cheatsheet.sh)"
    "[SYS] Neovim Isolado (Notas & Relatórios)"
    "[SYS] Definir Alvo (Scope Target)"
)

# Verifica se fzf está disponível
if command -v fzf >/dev/null 2>&1; then
    CHOICE=$(printf '%s\n' "${ITEMS[@]}" | fzf \
        --prompt="killerwhale::launcher > " \
        --header="[ ENTER: Executar | ESC: Cancelar ]" \
        --color="bg:#050a05,fg:#00ff66,hl:#66ff99,bg+:#003311,fg+:#ffffff,hl+:#66ff99,pointer:#00ff66,info:#008833,prompt:#00ff66,header:#00aa44" \
        --preview="bash '$KW_ROOT/launcher/preview.sh' {}" \
        --preview-window=right:50%:wrap \
        --height=85% \
        --layout=reverse \
        --border=sharp || true)
else
    # Fallback caso fzf não esteja presente
    clear 2>/dev/null || true
    echo -e "${KW_FG_GREEN}${KW_BOLD}=== KILLERWHALE COMMAND PALETTE ===${KW_RESET}"
    for i in "${!ITEMS[@]}"; do
        printf "${KW_FG_GREEN}[%2d]${KW_RESET} %s\n" "$((i+1))" "${ITEMS[$i]}"
    done
    echo ""
    echo -ne "${KW_FG_WHITE}Selecione a opção: ${KW_RESET}"
    read -r idx
    if [[ "$idx" =~ ^[0-9]+$ ]] && [ "$idx" -ge 1 ] && [ "$idx" -le "${#ITEMS[@]}" ]; then
        CHOICE="${ITEMS[$((idx-1))]}"
    else
        CHOICE=""
    fi
fi

[ -z "$CHOICE" ] && exit 0

case "$CHOICE" in
    *"[WS:00] Dashboard"*)
        switch_tmux_window "0" "00-dashboard" "bash '$KW_ROOT/workspaces/00-dashboard/dashboard.sh'"
        ;;
    *"[WS:01] Recon"*)
        switch_tmux_window "1" "01-recon" "bash '$KW_ROOT/workspaces/01-recon/recon.sh'"
        ;;
    *"[WS:02] Exploit"*)
        switch_tmux_window "2" "02-exploit" "bash '$KW_ROOT/workspaces/02-exploit/exploit.sh'"
        ;;
    *"[TOOL] Nmap Wrapper"*)
        run_in_tmux_or_exec "nmap-wrap" "python3 '$KW_ROOT/wrappers/nmap_wrap.py' --interactive; echo 'Pressione Enter para fechar...'; read -r"
        ;;
    *"[TOOL] Sqlmap Wrapper"*)
        run_in_tmux_or_exec "sqlmap-wrap" "python3 '$KW_ROOT/wrappers/sqlmap_wrap.py' --interactive; echo 'Pressione Enter para fechar...'; read -r"
        ;;
    *"[SYS] Monitor de Recursos (btop)"*)
        run_in_tmux_or_exec "btop" "btop --theme '$KW_ROOT/theme/btop.theme'"
        ;;
    *"[SYS] Limpeza do Sistema"*)
        run_in_tmux_or_exec "cleanup" "bash '$KW_ROOT/workspaces/00-dashboard/cleanup.sh'"
        ;;
    *"[SYS] Cheatsheet Browser"*)
        run_in_tmux_or_exec "cheatsheet" "bash '$KW_ROOT/workspaces/00-dashboard/cheatsheet.sh'"
        ;;
    *"[SYS] Neovim Isolado"*)
        run_in_tmux_or_exec "neovim" "XDG_CONFIG_HOME='$KW_ROOT' nvim '$KW_ROOT'"
        ;;
    *"[SYS] Definir Alvo"*)
        define_target
        ;;
esac

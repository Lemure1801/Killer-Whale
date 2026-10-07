#!/usr/bin/env bash
# ==============================================================================
# KillerWhale — Workspace 00: Dashboard Principal
# Resumo de Recursos, Telemetria do Sistema e Navegação Central
# ==============================================================================
set -u

KW_ROOT="${KW_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
TARGET_FILE="${HOME}/.killerwhale/target"

# Carrega a paleta central de cores se existir
if [ -f "$KW_ROOT/theme/colors.sh" ]; then
    # shellcheck source=/dev/null
    source "$KW_ROOT/theme/colors.sh"
else
    KW_RESET="\033[0m"
    KW_BOLD="\033[1m"
    KW_FG_GREEN="\033[38;2;0;255;102m"
    KW_FG_BRIGHT="\033[38;2;102;255;153m"
    KW_FG_DIM="\033[38;2;0;102;34m"
    KW_FG_AMBER="\033[38;2;255;176;0m"
    KW_FG_ALERT="\033[38;2;255;51;51m"
    KW_FG_WHITE="\033[38;2;240;255;240m"
fi

get_target() {
    if [ -f "$TARGET_FILE" ]; then
        local t
        t=$(cat "$TARGET_FILE" 2>/dev/null | tr -d '\n\r')
        if [ -n "$t" ]; then
            echo "$t"
            return
        fi
    fi
    echo "NÃO DEFINIDO"
}

set_target() {
    clear
    echo -e "${KW_FG_GREEN}${KW_BOLD}"
    echo "┌────────────────────────────────────────────────────────┐"
    echo "│         DEFINIR ALVO / ESCOPO DE AUDITORIA             │"
    echo "└────────────────────────────────────────────────────────┘${KW_RESET}"
    echo ""
    echo -ne "${KW_FG_WHITE}Digite o IP ou hostname do alvo (ou vazio para limpar): ${KW_FG_AMBER}"
    read -r new_target
    mkdir -p "$(dirname "$TARGET_FILE")"
    if [ -n "$new_target" ]; then
        echo "$new_target" > "$TARGET_FILE"
        echo -e "${KW_FG_BRIGHT}[✓] Alvo atualizado: $new_target${KW_RESET}"
    else
        rm -f "$TARGET_FILE"
        echo -e "${KW_FG_DIM}[i] Alvo limpo.${KW_RESET}"
    fi
    sleep 1
}

get_cpu_usage() {
    if command -v top >/dev/null 2>&1; then
        top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}' 2>/dev/null || echo "N/A"
    else
        awk '{print $1, $2, $3}' /proc/loadavg 2>/dev/null || echo "N/A"
    fi
}

get_mem_usage() {
    if command -v free >/dev/null 2>&1; then
        free -m | awk '/Mem:/ {printf "%dMB / %dMB (%d%%)", $3, $2, ($3/$2)*100}' 2>/dev/null || echo "N/A"
    else
        echo "N/A"
    fi
}

get_disk_usage() {
    df -h / 2>/dev/null | awk 'NR==2 {printf "%s / %s (%s)", $3, $2, $5}' || echo "N/A"
}

get_interfaces() {
    if command -v ip >/dev/null 2>&1; then
        ip -brief address show 2>/dev/null | grep -v "127.0.0.1" | awk '{print $1 ": " $3}' | tr '\n' ' | ' | sed 's/ | $//'
    else
        hostname -I 2>/dev/null || echo "127.0.0.1"
    fi
}

launch_btop() {
    if command -v btop >/dev/null 2>&1; then
        local btop_theme="$KW_ROOT/theme/btop.theme"
        if [ -f "$btop_theme" ]; then
            btop --theme "$btop_theme"
        else
            btop
        fi
    else
        echo -e "${KW_FG_ALERT}[!] btop não encontrado. Instale com: pacman -S btop${KW_RESET}"
        sleep 2
    fi
}

switch_workspace() {
    local target_win="$1"
    if [ -n "${TMUX:-}" ]; then
        tmux select-window -t ":$target_win" 2>/dev/null || true
    else
        echo -e "${KW_FG_AMBER}[!] Não executando dentro do tmux. Abrindo shell local...${KW_RESET}"
        sleep 1
    fi
}

while true; do
    clear
    target=$(get_target)
    cpu=$(get_cpu_usage)
    mem=$(get_mem_usage)
    disk=$(get_disk_usage)
    net=$(get_interfaces)
    net="${net:-Sem conexao externa}"
    uptime_str=$(uptime -p 2>/dev/null || uptime | awk -F, '{print $1}')
    kernel_str=$(uname -sr)
    hostname_str=$(hostname 2>/dev/null || echo "archlinux")

    echo -e "${KW_FG_GREEN}${KW_BOLD}"
    cat << "EOF"
  _  ___ _ _     __          ___           _      
 | |/ (_) | |    \ \        / / |         | |     
 | ' / _| | | ___ \ \  /\  / /| |__   __ _| | ___ 
 |  < | | | |/ _ \ \ \/  \/ / | '_ \ / _` | |/ _ \
 | . \| | | |  __/  \  /\  /  | | | | (_| | |  __/
 |_|\_\_|_|_|\___|   \/  \/   |_| |_|\__,_|_|\___|
EOF
    echo -e "${KW_FG_DIM}┌────────────────────────────────────────────────────────────────────────┐${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}  ${KW_FG_BRIGHT}${KW_BOLD}PAINEL DE CONTROLE TUI${KW_RESET} // ${KW_FG_WHITE}${hostname_str}${KW_RESET} (${KW_FG_DIM}${kernel_str}${KW_RESET})   ${KW_FG_GREEN}${uptime_str}${KW_RESET}"
    echo -e "${KW_FG_DIM}├────────────────────────────────────────────────────────────────────────┤${KW_RESET}"
    printf "${KW_FG_DIM}│${KW_RESET}  ${KW_FG_WHITE}%-16s${KW_RESET} : ${KW_FG_AMBER}%-50s${KW_RESET} ${KW_FG_DIM}│${KW_RESET}\n" "ALVO ATIVO" "$target"
    printf "${KW_FG_DIM}│${KW_RESET}  ${KW_FG_WHITE}%-16s${KW_RESET} : ${KW_FG_GREEN}%-50s${KW_RESET} ${KW_FG_DIM}│${KW_RESET}\n" "CPU (CARGA)" "$cpu"
    printf "${KW_FG_DIM}│${KW_RESET}  ${KW_FG_WHITE}%-16s${KW_RESET} : ${KW_FG_GREEN}%-50s${KW_RESET} ${KW_FG_DIM}│${KW_RESET}\n" "MEMÓRIA RAM" "$mem"
    printf "${KW_FG_DIM}│${KW_RESET}  ${KW_FG_WHITE}%-16s${KW_RESET} : ${KW_FG_GREEN}%-50s${KW_RESET} ${KW_FG_DIM}│${KW_RESET}\n" "DISCO RAIZ" "$disk"
    printf "${KW_FG_DIM}│${KW_RESET}  ${KW_FG_WHITE}%-16s${KW_RESET} : ${KW_FG_GREEN}%-50s${KW_RESET} ${KW_FG_DIM}│${KW_RESET}\n" "REDE ATIVA" "${net:0:50}"
    echo -e "${KW_FG_DIM}├────────────────────────────────────────────────────────────────────────┤${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}  ${KW_FG_BOLD}AÇÕES E WORKSPACES${KW_RESET}:                                                  ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[1]${KW_RESET} Ir para Workspace 01 (Recon)                                    ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[2]${KW_RESET} Ir para Workspace 02 (Exploit)                                  ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[b]${KW_RESET} Abrir Monitor Detalhado de Recursos (btop)                       ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[m]${KW_RESET} Abrir Launcher / Command Palette (fzf)                          ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[c]${KW_RESET} Manutenção e Limpeza do Sistema (cleanup.sh)                    ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[h]${KW_RESET} Cheatsheets & Guia de Comandos (cheatsheet.sh)                  ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[e]${KW_RESET} Abrir Editor Neovim (Auditoria / Relatórios)                    ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[t]${KW_RESET} Definir / Alterar Alvo Ativo                                    ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[r]${KW_RESET} Atualizar Telemetria                                            ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_ALERT}[q]${KW_RESET} Sair do Painel para Shell Interativo                           ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}└────────────────────────────────────────────────────────────────────────┘${KW_RESET}"
    echo ""
    echo -ne "${KW_FG_GREEN}${KW_BOLD}killerwhale::dashboard > ${KW_RESET}"
    read -r -n 1 -s opt || true
    echo ""

    case "$opt" in
        1)
            switch_workspace "1"
            ;;
        2)
            switch_workspace "2"
            ;;
        b|B)
            launch_btop
            ;;
        m|M)
            if [ -x "$KW_ROOT/launcher/menu.sh" ]; then
                bash "$KW_ROOT/launcher/menu.sh"
            fi
            ;;
        c|C)
            if [ -x "$KW_ROOT/workspaces/00-dashboard/cleanup.sh" ]; then
                bash "$KW_ROOT/workspaces/00-dashboard/cleanup.sh"
            else
                echo -e "${KW_FG_AMBER}[!] cleanup.sh ainda não disponível ou sem permissão.${KW_RESET}"
                sleep 1
            fi
            ;;
        h|H)
            if [ -x "$KW_ROOT/workspaces/00-dashboard/cheatsheet.sh" ]; then
                bash "$KW_ROOT/workspaces/00-dashboard/cheatsheet.sh"
            else
                echo -e "${KW_FG_AMBER}[!] cheatsheet.sh ainda não disponível.${KW_RESET}"
                sleep 1
            fi
            ;;
        e|E)
            XDG_CONFIG_HOME="$KW_ROOT" nvim "$KW_ROOT"
            ;;
        t|T)
            set_target
            ;;
        r|R)
            continue
            ;;
        q|Q)
            echo -e "${KW_FG_DIM}Encerrando painel do dashboard...${KW_RESET}"
            break
            ;;
        *)
            # Qualquer outra tecla apenas recarrega
            continue
            ;;
    esac
done

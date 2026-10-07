#!/usr/bin/env bash
# ==============================================================================
# KillerWhale — Workspace 00: Limpeza e Manutenção do Sistema
# Higienização de caches, logs do journal, SSD TRIM e logs temporários
# ==============================================================================
set -u

KW_ROOT="${KW_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# shellcheck source=/dev/null
[ -f "$KW_ROOT/theme/colors.sh" ] && source "$KW_ROOT/theme/colors.sh"

confirm_action() {
    local prompt_msg="$1"
    echo -ne "${KW_FG_AMBER}[?] ${prompt_msg} (s/N): ${KW_RESET}"
    read -r resp
    case "$resp" in
        [sS]|[yY]|[sS][iI][mM]) return 0 ;;
        *) return 1 ;;
    esac
}

clean_pacman_cache() {
    echo -e "\n${KW_FG_GREEN}=== [1] LIMPEZA DO CACHE DO PACMAN ===${KW_RESET}"
    echo -e "${KW_FG_DIM}Remove versões antigas de pacotes baixados pelo pacman (/var/cache/pacman/pkg).${KW_RESET}"
    if confirm_action "Deseja limpar versões antigas do cache do pacman?"; then
        if command -v paccache >/dev/null 2>&1; then
            echo -e "${KW_FG_WHITE}[*] Executando: sudo paccache -rk2${KW_RESET}"
            sudo paccache -rk2 || true
        else
            echo -e "${KW_FG_WHITE}[*] Executando: sudo pacman -Sc --noconfirm${KW_RESET}"
            sudo pacman -Sc --noconfirm || true
        fi
        echo -e "${KW_FG_BRIGHT}[✓] Limpeza do cache do pacman concluída.${KW_RESET}"
    else
        echo -e "${KW_FG_DIM}[i] Operação cancelada.${KW_RESET}"
    fi
}

clean_orphans() {
    echo -e "\n${KW_FG_GREEN}=== [2] REMOÇÃO DE PACOTES ÓRFÃOS ===${KW_RESET}"
    echo -e "${KW_FG_DIM}Identifica e remove dependências não mais necessárias no Arch Linux.${KW_RESET}"
    orphans=$(pacman -Qtdq 2>/dev/null || true)
    if [ -z "$orphans" ]; then
        echo -e "${KW_FG_BRIGHT}[✓] Nenhum pacote órfão encontrado no sistema.${KW_RESET}"
        return
    fi
    echo -e "${KW_FG_AMBER}Pacotes órfãos encontrados:${KW_RESET} $orphans"
    if confirm_action "Deseja remover estes pacotes órfãos?"; then
        echo -e "${KW_FG_WHITE}[*] Removendo pacotes...${KW_RESET}"
        # shellcheck disable=SC2086
        sudo pacman -Rns $orphans --noconfirm || true
        echo -e "${KW_FG_BRIGHT}[✓] Pacotes órfãos removidos.${KW_RESET}"
    else
        echo -e "${KW_FG_DIM}[i] Operação cancelada.${KW_RESET}"
    fi
}

vacuum_journal() {
    echo -e "\n${KW_FG_GREEN}=== [3] VACUUM DE LOGS DO SYSTEMD JOURNAL ===${KW_RESET}"
    echo -e "${KW_FG_DIM}Limpa registros do journalctl mantendo apenas os últimos 3 dias.${KW_RESET}"
    if confirm_action "Deseja truncar os logs do journalctl para os últimos 3 dias?"; then
        echo -e "${KW_FG_WHITE}[*] Executando: sudo journalctl --vacuum-time=3d${KW_RESET}"
        sudo journalctl --vacuum-time=3d || true
        echo -e "${KW_FG_BRIGHT}[✓] Logs truncados com sucesso.${KW_RESET}"
    else
        echo -e "${KW_FG_DIM}[i] Operação cancelada.${KW_RESET}"
    fi
}

run_fstrim() {
    echo -e "\n${KW_FG_GREEN}=== [4] EXECUÇÃO DE SSD FSTRIM ===${KW_RESET}"
    echo -e "${KW_FG_DIM}Descarta blocos não utilizados em sistemas de arquivos montados (SSD/NVMe/Discos Virtuais).${KW_RESET}"
    if confirm_action "Deseja executar fstrim em todas as partições montadas?"; then
        echo -e "${KW_FG_WHITE}[*] Executando: sudo fstrim -va${KW_RESET}"
        sudo fstrim -va || true
        echo -e "${KW_FG_BRIGHT}[✓] Operação de TRIM concluída.${KW_RESET}"
    else
        echo -e "${KW_FG_DIM}[i] Operação cancelada.${KW_RESET}"
    fi
}

clean_kw_logs() {
    echo -e "\n${KW_FG_GREEN}=== [5] LIMPEZA DE LOGS DE AUDITORIA DO KILLERWHALE ===${KW_RESET}"
    local log_dir="${KW_LOG_DIR:-$HOME/.killerwhale/logs}"
    echo -e "${KW_FG_DIM}Diretório de logs: $log_dir${KW_RESET}"
    if [ ! -d "$log_dir" ] || [ -z "$(ls -A "$log_dir" 2>/dev/null)" ]; then
        echo -e "${KW_FG_BRIGHT}[✓] Nenhum arquivo de log para remover.${KW_RESET}"
        return
    fi
    echo -e "${KW_FG_AMBER}Arquivos encontrados:${KW_RESET}"
    ls -lh "$log_dir"
    if confirm_action "Deseja excluir TODOS os logs de auditoria acima?"; then
        rm -f "$log_dir"/*.log
        echo -e "${KW_FG_BRIGHT}[✓] Logs de auditoria removidos.${KW_RESET}"
    else
        echo -e "${KW_FG_DIM}[i] Operação cancelada.${KW_RESET}"
    fi
}

clean_tool_caches() {
    echo -e "\n${KW_FG_GREEN}=== [6] LIMPEZA DE CACHE DE FERRAMENTAS ESPECÍFICAS ===${KW_RESET}"
    echo -e "${KW_FG_DIM}Remove saídas e relatórios antigos de ferramentas como sqlmap (~/.local/share/sqlmap/output).${KW_RESET}"
    local sqlmap_out="${HOME}/.local/share/sqlmap/output"
    if [ -d "$sqlmap_out" ]; then
        echo -e "Encontrado diretório: $sqlmap_out"
        if confirm_action "Deseja limpar o cache de output do sqlmap?"; then
            rm -rf "${sqlmap_out:?}"/*
            echo -e "${KW_FG_BRIGHT}[✓] Cache do sqlmap limpo.${KW_RESET}"
        fi
    else
        echo -e "${KW_FG_DIM}[i] Diretório do sqlmap não contém dados acumulados.${KW_RESET}"
    fi
}

while true; do
    clear
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
    echo -e "${KW_FG_DIM}│${KW_RESET}  ${KW_FG_BRIGHT}${KW_BOLD}CENTRAL DE HIGIENIZAÇÃO & LIMPEZA DO SISTEMA${KW_RESET}                       ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}├────────────────────────────────────────────────────────────────────────┤${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[1]${KW_RESET} Limpar Cache de Pacotes do Pacman (paccache / pacman -Sc)        ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[2]${KW_RESET} Remover Pacotes Órfãos (pacman -Qtdq)                            ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[3]${KW_RESET} Vacuum de Logs do Systemd Journal (journalctl --vacuum-time=3d)  ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[4]${KW_RESET} Executar TRIM em Unidades de Armazenamento (fstrim -va)          ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[5]${KW_RESET} Limpar Logs de Auditoria do KillerWhale                         ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[6]${KW_RESET} Limpar Caches de Ferramentas de Auditoria (ex: sqlmap output)   ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_GREEN}[a]${KW_RESET} Executar TODAS as Limpezas Acima (com confirmação individual)    ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}│${KW_RESET}   ${KW_FG_ALERT}[q]${KW_RESET} Retornar ao Dashboard Principal                                 ${KW_FG_DIM}│${KW_RESET}"
    echo -e "${KW_FG_DIM}└────────────────────────────────────────────────────────────────────────┘${KW_RESET}"
    echo ""
    echo -ne "${KW_FG_GREEN}${KW_BOLD}killerwhale::cleanup > ${KW_RESET}"
    read -r opt || true

    case "$opt" in
        1) clean_pacman_cache ;;
        2) clean_orphans ;;
        3) vacuum_journal ;;
        4) run_fstrim ;;
        5) clean_kw_logs ;;
        6) clean_tool_caches ;;
        a|A)
            clean_pacman_cache
            clean_orphans
            vacuum_journal
            run_fstrim
            clean_kw_logs
            clean_tool_caches
            ;;
        q|Q) break ;;
        *) continue ;;
    esac

    echo ""
    echo -ne "${KW_FG_DIM}Pressione ENTER para continuar...${KW_RESET}"
    read -r
done

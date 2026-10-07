#!/usr/bin/env bash
# ==============================================================================
# KillerWhale — Preview Engine para o Launcher (fzf)
# ==============================================================================
set -euo pipefail

KW_ROOT="${KW_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# shellcheck source=/dev/null
[ -f "$KW_ROOT/theme/colors.sh" ] && source "$KW_ROOT/theme/colors.sh"

selected="${1:-}"

echo -e "${KW_FG_GREEN}${KW_BOLD}"
cat << "EOF"
  _  ___ _ _     __          ___           _      
 | |/ (_) | |    \ \        / / |         | |     
 | ' / _| | | ___ \ \  /\  / /| |__   __ _| | ___ 
 |  < | | | |/ _ \ \ \/  \/ / | '_ \ / _` | |/ _ \
 | . \| | | |  __/  \  /\  /  | | | | (_| | |  __/
 |_|\_\_|_|_|\___|   \/  \/   |_| |_|\__,_|_|\___|
EOF
echo -e "${KW_RESET}"

case "$selected" in
    *"[WS:00] Dashboard"*)
        echo -e "${KW_FG_BRIGHT}${KW_BOLD}=== WORKSPACE 00: DASHBOARD ===${KW_RESET}"
        echo -e "${KW_FG_WHITE}Finalidade:${KW_RESET} Painel principal de telemetria e controle do sistema."
        echo -e "${KW_FG_WHITE}Recursos:${KW_RESET} Exibe CPU, Memória, Disco, Rede e Alvo ativo."
        echo -e "${KW_FG_WHITE}Atalho no tmux:${KW_RESET} ${KW_FG_AMBER}Prefix + 0${KW_RESET}"
        echo -e "${KW_FG_DIM}Script: workspaces/00-dashboard/dashboard.sh${KW_RESET}"
        ;;
    *"[WS:01] Recon"*)
        echo -e "${KW_FG_BRIGHT}${KW_BOLD}=== WORKSPACE 01: RECONHECIMENTO ===${KW_RESET}"
        echo -e "${KW_FG_WHITE}Finalidade:${KW_RESET} Espaço de trabalho para enumeração de alvos e serviços."
        echo -e "${KW_FG_WHITE}Ferramentas:${KW_RESET} nmap_wrap.py, dig, whois, curl."
        echo -e "${KW_FG_WHITE}Atalho no tmux:${KW_RESET} ${KW_FG_AMBER}Prefix + 1${KW_RESET}"
        echo -e "${KW_FG_DIM}Diretório: workspaces/01-recon/${KW_RESET}"
        ;;
    *"[WS:02] Exploit"*)
        echo -e "${KW_FG_BRIGHT}${KW_BOLD}=== WORKSPACE 02: EXPLOIT & AUDITORIA ===${KW_RESET}"
        echo -e "${KW_FG_WHITE}Finalidade:${KW_RESET} Testes controlados e validação de vulnerabilidades."
        echo -e "${KW_FG_WHITE}Ferramentas:${KW_RESET} sqlmap_wrap.py, scripts de verificação."
        echo -e "${KW_FG_WHITE}Atalho no tmux:${KW_RESET} ${KW_FG_AMBER}Prefix + 2${KW_RESET}"
        echo -e "${KW_FG_DIM}Diretório: workspaces/02-exploit/${KW_RESET}"
        ;;
    *"[TOOL] Nmap Wrapper"*)
        echo -e "${KW_FG_BRIGHT}${KW_BOLD}=== NMAP WRAPPER (Python / Rich) ===${KW_RESET}"
        echo -e "${KW_FG_WHITE}Finalidade:${KW_RESET} Varredura de portas com saída tabular em ASCII Rich."
        echo -e "${KW_FG_WHITE}Logs:${KW_RESET} Salva automaticamente em ${KW_FG_AMBER}\$KW_ROOT/logs/nmap_*.log${KW_RESET}"
        echo -e "${KW_FG_WHITE}Uso CLI:${KW_RESET} nmap_wrap.py <IP/Host> [argumentos do nmap]"
        echo -e "${KW_FG_DIM}Script: wrappers/nmap_wrap.py${KW_RESET}"
        ;;
    *"[TOOL] Sqlmap Wrapper"*)
        echo -e "${KW_FG_BRIGHT}${KW_BOLD}=== SQLMAP WRAPPER (Python / Rich) ===${KW_RESET}"
        echo -e "${KW_FG_WHITE}Finalidade:${KW_RESET} Execução estruturada para testes controlados de injeção."
        echo -e "${KW_FG_WHITE}Logs:${KW_RESET} Salva automaticamente em ${KW_FG_AMBER}\$KW_ROOT/logs/sqlmap_*.log${KW_RESET}"
        echo -e "${KW_FG_WHITE}Uso CLI:${KW_RESET} sqlmap_wrap.py -u <URL> [opções]"
        echo -e "${KW_FG_DIM}Script: wrappers/sqlmap_wrap.py${KW_RESET}"
        ;;
    *"[SYS] Monitor de Recursos (btop)"*)
        echo -e "${KW_FG_BRIGHT}${KW_BOLD}=== MONITOR DE RECURSOS (BTOP) ===${KW_RESET}"
        echo -e "${KW_FG_WHITE}Finalidade:${KW_RESET} Monitor de processos, CPU, I/O e tráfego de rede em tempo real."
        echo -e "${KW_FG_WHITE}Estética:${KW_RESET} Tema KillerWhale fósforo verde aplicado nativamente."
        echo -e "${KW_FG_WHITE}Atalho no tmux:${KW_RESET} ${KW_FG_AMBER}Prefix + b${KW_RESET} (ou via dashboard)"
        ;;
    *"[SYS] Limpeza do Sistema (cleanup.sh)"*)
        echo -e "${KW_FG_BRIGHT}${KW_BOLD}=== LIMPEZA E MANUTENÇÃO ===${KW_RESET}"
        echo -e "${KW_FG_WHITE}Finalidade:${KW_RESET} Higienização de cache pacman, vacuum do journal e logs temporários."
        echo -e "${KW_FG_WHITE}Segurança:${KW_RESET} Exige confirmação prévia para cada ação."
        echo -e "${KW_FG_WHITE}Atalho no tmux:${KW_RESET} ${KW_FG_AMBER}Prefix + k${KW_RESET}"
        ;;
    *"[SYS] Cheatsheet Browser"*)
        echo -e "${KW_FG_BRIGHT}${KW_BOLD}=== GUIA DE COMANDOS (CHEATSHEETS) ===${KW_RESET}"
        echo -e "${KW_FG_WHITE}Finalidade:${KW_RESET} Navegação rápida em comandos e parâmetros de pentest."
        echo -e "${KW_FG_WHITE}Fonte:${KW_RESET} Arquivos em Markdown de ${KW_FG_AMBER}cheatsheets/*.md${KW_RESET}"
        echo -e "${KW_FG_WHITE}Atalho no tmux:${KW_RESET} ${KW_FG_AMBER}Prefix + ?${KW_RESET}"
        ;;
    *"[SYS] Neovim Isolado"*)
        echo -e "${KW_FG_BRIGHT}${KW_BOLD}=== NEOVIM (AMBIENTE ISOLADO) ===${KW_RESET}"
        echo -e "${KW_FG_WHITE}Finalidade:${KW_RESET} Edição de notas de pentest, relatórios e scripts."
        echo -e "${KW_FG_WHITE}Isolamento:${KW_RESET} Não interfere em dotfiles pessoais (~/.config/nvim mantido intacto)."
        echo -e "${KW_FG_WHITE}Atalho no tmux:${KW_RESET} ${KW_FG_AMBER}Prefix + e${KW_RESET}"
        ;;
    *"[SYS] Definir Alvo"*)
        echo -e "${KW_FG_BRIGHT}${KW_BOLD}=== DEFINIR ESCOPO / ALVO ATIVO ===${KW_RESET}"
        echo -e "${KW_FG_WHITE}Finalidade:${KW_RESET} Configura o IP ou domínio do alvo na barra de status e wrappers."
        echo -e "${KW_FG_WHITE}Armazenamento:${KW_RESET} Gravado em ~/.killerwhale/target."
        ;;
    *)
        echo -e "${KW_FG_DIM}Selecione um item na lista à esquerda para visualizar detalhes e opções.${KW_RESET}"
        ;;
esac

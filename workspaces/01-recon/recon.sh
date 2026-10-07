#!/usr/bin/env bash
# ==============================================================================
# KillerWhale — Workspace 01: Recon
# Ponto de entrada para reconhecimento de rede, portas e serviços
# ==============================================================================
set -euo pipefail

KW_ROOT="${KW_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
TARGET_FILE="${HOME}/.killerwhale/target"

# shellcheck source=/dev/null
source "$KW_ROOT/theme/colors.sh"

clear
kw_banner
echo -e "${KW_FG_GREEN}┌─[ ${KW_BOLD}WORKSPACE 01: RECONHECIMENTO & ENUMERAÇÃO${KW_RESET}${KW_FG_GREEN} ]──────────────────┐${KW_RESET}"
target="NÃO DEFINIDO"
if [ -f "$TARGET_FILE" ]; then
    target=$(cat "$TARGET_FILE" 2>/dev/null || echo "NÃO DEFINIDO")
fi
echo -e "${KW_FG_GREEN}│${KW_RESET}  ${KW_FG_WHITE}Alvo Ativo:${KW_RESET} ${KW_FG_AMBER}${target}${KW_RESET}"
echo -e "${KW_FG_GREEN}│${KW_RESET}  ${KW_FG_DIM}Wrappers disponíveis: nmap_wrap.py${KW_RESET}"
echo -e "${KW_FG_GREEN}│${KW_RESET}  ${KW_FG_DIM}Atalhos: 'kw' (Launcher), 'kw-dash' (Dashboard), 'kw-cheat' (Cheatsheet)${KW_RESET}"
echo -e "${KW_FG_GREEN}└────────────────────────────────────────────────────────────────────────┘${KW_RESET}"
echo ""

# Inicia fish se disponível, caso contrário bash
if command -v fish >/dev/null 2>&1; then
    exec fish
else
    exec bash
fi

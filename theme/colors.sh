#!/usr/bin/env bash
# ==============================================================================
# KillerWhale — Paleta Central de Cores e Estilo Visual
# Estética: Terminal CRT Fósforo Verde / Monocromático de Alto Contraste
# ==============================================================================

# Definições Hexadecimais (para configs de emuladores e apps externos)
export KW_HEX_BG="#050a05"          # Fundo quase negro profundo com leve tom esmeralda
export KW_HEX_FG="#00ff66"          # Fósforo verde primário de alta luminosidade
export KW_HEX_FG_BRIGHT="#66ff99"   # Verde brilhante para destaques
export KW_HEX_FG_DIM="#006622"      # Verde escuro / bordas atenuadas
export KW_HEX_WHITE="#f0fff0"       # Branco menta para texto de alto contraste
export KW_HEX_ACCENT="#ffb000"      # Âmbar para avisos e telemetria
export KW_HEX_ALERT="#ff3333"       # Vermelho fósforo para erros críticos
export KW_HEX_GRAY="#1a2e1a"        # Linhas divisórias e caixas secundárias

# Códigos ANSI Escape (Bash / Shell)
export KW_RESET="\033[0m"
export KW_BOLD="\033[1m"
export KW_DIM="\033[2m"
export KW_ITALIC="\033[3m"
export KW_UNDERLINE="\033[4m"

# Cores de Texto (Foreground)
export KW_FG_GREEN="\033[38;2;0;255;102m"
export KW_FG_BRIGHT="\033[38;2;102;255;153m"
export KW_FG_DIM="\033[38;2;0;102;34m"
export KW_FG_WHITE="\033[38;2;240;255;240m"
export KW_FG_AMBER="\033[38;2;255;176;0m"
export KW_FG_ALERT="\033[38;2;255;51;51m"
export KW_FG_GRAY="\033[38;2;90;120;90m"

# Cores de Fundo (Background)
export KW_BG_DARK="\033[48;2;5;10;5m"
export KW_BG_HL="\033[48;2;15;35;15m"

# Funções Auxiliares de Formatação e Box-Drawing
kw_banner() {
    echo -e "${KW_FG_GREEN}${KW_BOLD}"
    cat << "EOF"
  _  ___ _ _     __          ___           _      
 | |/ (_) | |    \ \        / / |         | |     
 | ' / _| | | ___ \ \  /\  / /| |__   __ _| | ___ 
 |  < | | | |/ _ \ \ \/  \/ / | '_ \ / _` | |/ _ \
 | . \| | | |  __/  \  /\  /  | | | | (_| | |  __/
 |_|\_\_|_|_|\___|   \/  \/   |_| |_|\__,_|_|\___|
EOF
    echo -e "${KW_FG_DIM} [ WORKSPACE TUI // ARCH LINUX PENTEST ENVIRONMENT ]${KW_RESET}"
    echo ""
}

kw_box() {
    local title="$1"
    local content="$2"
    local width=64
    echo -e "${KW_FG_GREEN}┌─[ ${KW_BOLD}${title}${KW_RESET}${KW_FG_GREEN} ]$(printf '─%.0s' $(seq 1 $((width - ${#title} - 6))))┐${KW_RESET}"
    while IFS= read -r line; do
        printf "${KW_FG_GREEN}│${KW_RESET} %-$((width - 4))s ${KW_FG_GREEN}│${KW_RESET}\n" "$line"
    done <<< "$content"
    echo -e "${KW_FG_GREEN}└$(printf '─%.0s' $(seq 1 $((width - 2))))┘${KW_RESET}"
}

kw_info() {
    echo -e "${KW_FG_GREEN}[i]${KW_RESET} $1"
}

kw_success() {
    echo -e "${KW_FG_BRIGHT}[✓]${KW_RESET} $1"
}

kw_warn() {
    echo -e "${KW_FG_AMBER}[!]${KW_RESET} $1"
}

kw_error() {
    echo -e "${KW_FG_ALERT}[✗]${KW_RESET} $1"
}

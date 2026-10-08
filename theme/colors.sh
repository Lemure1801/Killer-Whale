#!/usr/bin/env bash
# ==============================================================================
# KillerWhale — Paleta Central de Cores e Estilo Visual
# Estética: Terminal CRT Fósforo Verde / Monocromático de Alto Contraste
# ==============================================================================

# Definições Hexadecimais (para configs de emuladores e apps externos)
export KW_HEX_BG="#000000"          # Fundo preto absoluto
export KW_HEX_FG="#00ffd1"          # Ciano/verde-água fosforescente primário
export KW_HEX_FG_BRIGHT="#4dffef"   # Ciano brilhante para destaques intensos
export KW_HEX_FG_DIM="#00594d"      # Ciano escuro / bordas atenuadas
export KW_HEX_WHITE="#e6ffff"       # Branco ciano luminoso para texto de alto contraste
export KW_HEX_ACCENT="#00b398"      # Ciano intermediário para telemetria
export KW_HEX_ALERT="#ff3355"       # Alerta / erros críticos
export KW_HEX_GRAY="#002620"        # Linhas divisórias e caixas secundárias
export KW_HEX_SURFACE="#050e0c"     # Superfície de cards e painéis

# Códigos ANSI Escape (Bash / Shell)
export KW_RESET="\033[0m"
export KW_BOLD="\033[1m"
export KW_DIM="\033[2m"
export KW_ITALIC="\033[3m"
export KW_UNDERLINE="\033[4m"

# Cores de Texto (Foreground)
export KW_FG_GREEN="\033[38;2;0;255;209m"
export KW_FG_CYAN="\033[38;2;0;255;209m"
export KW_FG_BRIGHT="\033[38;2;77;255;239m"
export KW_FG_DIM="\033[38;2;0;89;77m"
export KW_FG_WHITE="\033[38;2;230;255;255m"
export KW_FG_AMBER="\033[38;2;0;179;152m"
export KW_FG_ALERT="\033[38;2;255;51;85m"
export KW_FG_GRAY="\033[38;2;0;89;77m"

# Cores de Fundo (Background)
export KW_BG_DARK="\033[48;2;0;0;0m"
export KW_BG_HL="\033[48;2;0;51;43m"


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

#!/usr/bin/env bash
# ==============================================================================
# KillerWhale — Workspace 00: Navegador de Cheatsheets (fzf)
# Visualizador de referência rápida de comandos e parâmetros
# ==============================================================================
set -euo pipefail

KW_ROOT="${KW_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
CHEATS_DIR="$KW_ROOT/cheatsheets"

# shellcheck source=/dev/null
[ -f "$KW_ROOT/theme/colors.sh" ] && source "$KW_ROOT/theme/colors.sh"

if [ ! -d "$CHEATS_DIR" ]; then
    echo -e "${KW_FG_ALERT}[!] Diretório de cheatsheets não encontrado: $CHEATS_DIR${KW_RESET}"
    exit 1
fi

preview_cmd() {
    local file="$1"
    if command -v bat >/dev/null 2>&1; then
        bat --style=plain --color=always --language=markdown "$file"
    else
        cat "$file"
    fi
}

export -f preview_cmd

# Verifica se fzf está disponível
if command -v fzf >/dev/null 2>&1; then
    SELECTED_FILE=$(find "$CHEATS_DIR" -name "*.md" -type f -printf "%f\n" | sort | fzf \
        --prompt="killerwhale::cheatsheet > " \
        --header="[ ENTER: Ler Cheatsheet Completo | ESC: Sair ]" \
        --color="bg:#050a05,fg:#00ff66,hl:#66ff99,bg+:#003311,fg+:#ffffff,hl+:#66ff99,pointer:#00ff66,info:#008833,prompt:#00ff66,header:#00aa44" \
        --preview="bash -c 'preview_cmd \"$CHEATS_DIR/{}\"'" \
        --preview-window=right:65%:wrap \
        --height=90% \
        --layout=reverse \
        --border=sharp || true)

    if [ -n "$SELECTED_FILE" ]; then
        clear
        FULL_PATH="$CHEATS_DIR/$SELECTED_FILE"
        if command -v bat >/dev/null 2>&1; then
            bat --style=grid --theme=Monokai "$FULL_PATH"
        else
            less -R "$FULL_PATH"
        fi
    fi
else
    # Fallback simples caso fzf não esteja presente
    clear
    echo -e "${KW_FG_GREEN}${KW_BOLD}=== GUIA DE COMANDOS (CHEATSHEETS) ===${KW_RESET}"
    files=("$CHEATS_DIR"/*.md)
    for i in "${!files[@]}"; do
        printf "${KW_FG_GREEN}[%d]${KW_RESET} %s\n" "$((i+1))" "$(basename "${files[$i]}")"
    done
    echo ""
    echo -ne "${KW_FG_WHITE}Escolha um arquivo para visualizar [1-${#files[@]}]: ${KW_RESET}"
    read -r idx
    if [[ "$idx" =~ ^[0-9]+$ ]] && [ "$idx" -ge 1 ] && [ "$idx" -le "${#files[@]}" ]; then
        less "${files[$((idx-1))]}"
    fi
fi

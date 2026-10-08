#!/usr/bin/env bash
# ==============================================================================
# KillerWhale — Script de Bootstrap e Instalação Idempotente (Arch Linux)
# AVISO: Este script deve ser executado exclusivamente dentro da VM Arch Linux.
# ==============================================================================
set -euo pipefail

KW_ROOT="${KW_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
DRY_RUN=false

# Argumentos de linha de comando
for arg in "$@"; do
    case "$arg" in
        --dry-run)
            DRY_RUN=true
            ;;
        --help|-h)
            echo "Uso: $0 [--dry-run]"
            echo "  --dry-run : Exibe as ações sem alterar pacotes ou arquivos no sistema."
            exit 0
            ;;
    esac
done

# shellcheck source=/dev/null
[ -f "$KW_ROOT/theme/colors.sh" ] && source "$KW_ROOT/theme/colors.sh"

log_step() {
    echo -e "${KW_FG_GREEN}${KW_BOLD}[+] ${KW_RESET}${KW_FG_WHITE}$1${KW_RESET}"
}

log_ok() {
    echo -e "    ${KW_FG_BRIGHT}[✓] $1${KW_RESET}"
}

log_warn() {
    echo -e "    ${KW_FG_AMBER}[!] $1${KW_RESET}"
}

log_info() {
    echo -e "    ${KW_FG_DIM}[i] $1${KW_RESET}"
}

clear 2>/dev/null || true
kw_banner

echo -e "${KW_FG_GREEN}┌─[ ${KW_BOLD}INICIALIZANDO INSTALAÇÃO DO KILLERWHALE NO ARCH LINUX${KW_RESET}${KW_FG_GREEN} ]────────┐${KW_RESET}"
if [ "$DRY_RUN" = true ]; then
    echo -e "${KW_FG_GREEN}│${KW_RESET}  ${KW_FG_AMBER}MODO DRY-RUN ATIVADO: Nenhuma alteração real será feita.${KW_RESET}"
fi
echo -e "${KW_FG_GREEN}│${KW_RESET}  ${KW_FG_WHITE}Diretório Raiz:${KW_RESET} $KW_ROOT"
echo -e "${KW_FG_GREEN}└────────────────────────────────────────────────────────────────────────┘${KW_RESET}\n"

# 1. Validação do Sistema Operacional (Arch Linux)
log_step "1/6. Verificando distribuição hospedeira..."
if [ -f /etc/arch-release ] || ( [ -f /etc/os-release ] && grep -qi "arch" /etc/os-release ); then
    log_ok "Ambiente Arch Linux confirmado."
else
    log_warn "Aviso: Distribuição não identificada estritamente como Arch Linux."
    echo -ne "    ${KW_FG_AMBER}Deseja continuar mesmo assim? (s/N): ${KW_RESET}"
    if [ "$DRY_RUN" = false ]; then
        read -r resp
        case "$resp" in
            [sS]|[yY]|[sS][iI][mM]) ;;
            *) echo "Instalação abortada."; exit 1 ;;
        esac
    else
        echo "[DRY-RUN] Pulando confirmação interativa."
    fi
fi

# 2. Lista de Pacotes Oficiais Necessários
log_step "2/6. Identificando e instalando pacotes oficiais via pacman..."
PACMAN_PACKAGES=(
    # Interface e multiplexador
    tmux
    fzf
    btop
    neovim
    fish
    dialog
    
    # Manipulação de texto e utilitários modernos
    ripgrep
    fd
    bat
    jq
    git
    curl

    # Ambiente Python
    python
    python-pip
    python-rich

    # Rede e ferramentas de auditoria padrão
    nmap
    sqlmap
    iproute2
    bind
    net-tools
)

# Determina comando de elevação de privilégio se necessário
SUDO_CMD=""
if [ "$(id -u)" -ne 0 ]; then
    if command -v sudo >/dev/null 2>&1; then
        SUDO_CMD="sudo"
    elif command -v doas >/dev/null 2>&1; then
        SUDO_CMD="doas"
    else
        log_warn "Aviso: Nem 'sudo' nem 'doas' encontrados. Tentando executar pacman diretamente..."
    fi
fi

if [ "$DRY_RUN" = true ]; then
    log_info "[DRY-RUN] Executaria: ${SUDO_CMD:+$SUDO_CMD }pacman -S --needed --noconfirm ${PACMAN_PACKAGES[*]}"
else
    echo -e "    ${KW_FG_DIM}Instalando pacotes essenciais via pacman...${KW_RESET}"
    ${SUDO_CMD} pacman -S --needed --noconfirm "${PACMAN_PACKAGES[@]}"
    log_ok "Pacotes oficiais do sistema instalados/atualizados."
fi

# 3. Dependências Python da Nova Engine (Textual, Pynvim, Psutil)
log_step "3/7. Instalando dependências do motor Textual & RPC Neovim..."
PYTHON_DEPS=(
    textual
    pynvim
    psutil
    rich
    pillow
    rich-pixels
)
if [ "$DRY_RUN" = true ]; then
    log_info "[DRY-RUN] Executaria: pip install --break-system-packages ${PYTHON_DEPS[*]}"
else
    pip install --break-system-packages "${PYTHON_DEPS[@]}" || pip install --user "${PYTHON_DEPS[@]}" || log_warn "Não foi possível instalar via pip global/user; utilize o ambiente virtual do KillerWhale."
    log_ok "Dependências Python da interface e RPC configuradas."
fi

# 4. Pacotes Complementares / AUR (gum para TUI avançada)
log_step "4/7. Verificando utilitários interativos avançados (gum)..."
if command -v gum >/dev/null 2>&1; then
    log_ok "Utilitário 'gum' já disponível."
else
    if command -v yay >/dev/null 2>&1; then
        if [ "$DRY_RUN" = true ]; then
            log_info "[DRY-RUN] Executaria: yay -S --needed --noconfirm gum"
        else
            yay -S --needed --noconfirm gum || log_warn "Não foi possível instalar gum via yay; fallback para dialog/bash ativado."
        fi
    else
        log_info "AUR helper 'yay' não encontrado. Menus usarão fallback robusto em dialog/bash puro."
    fi
fi

# 5. Criação da Estrutura de Diretórios de Runtime
log_step "5/7. Configurando diretórios locais de auditoria e runtime..."
LOG_DIR="${HOME}/.killerwhale/logs"
TARGET_DIR="${HOME}/.killerwhale"

if [ "$DRY_RUN" = true ]; then
    log_info "[DRY-RUN] Criaria diretórios: $LOG_DIR e $TARGET_DIR"
else
    mkdir -p "$LOG_DIR"
    mkdir -p "$KW_ROOT/logs"
    if [ ! -f "$TARGET_DIR/target" ]; then
        touch "$TARGET_DIR/target"
    fi
    log_ok "Estrutura ~/.killerwhale/ pronta."
fi

# 6. Aplicação Idempotente de Symlinks (com Backup de Preexistentes)
log_step "6/7. Vinculando dotfiles (symlinks com backup preventivo)..."

link_file() {
    local src="$1"
    local dest="$2"

    if [ ! -f "$src" ]; then
        log_warn "Arquivo de origem não existe: $src"
        return
    fi

    local dest_dir
    dest_dir=$(dirname "$dest")
    [ "$DRY_RUN" = false ] && mkdir -p "$dest_dir"

    # Se já é o symlink correto, nada a fazer (idempotência)
    if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$src" ]; then
        log_ok "Symlink já atualizado: $dest -> $src"
        return
    fi

    # Se já existe como arquivo real ou link diferente, faz backup
    if [ -e "$dest" ] || [ -L "$dest" ]; then
        local bkp="${dest}.bak.$(date +%Y%m%d_%H%M%S)"
        if [ "$DRY_RUN" = true ]; then
            log_info "[DRY-RUN] Faria backup de $dest para $bkp"
        else
            mv "$dest" "$bkp"
            log_warn "Arquivo preexistente preservado: $bkp"
        fi
    fi

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY-RUN] Criaria symlink: $dest -> $src"
    else
        ln -s "$src" "$dest"
        log_ok "Symlink criado: $dest -> $src"
    fi
}

# Tmux
link_file "$KW_ROOT/tmux/tmux.conf" "$HOME/.tmux.conf"

# Fish Shell
link_file "$KW_ROOT/config.fish" "$HOME/.config/fish/config.fish"

# Alacritty (se diretório ou binário existir)
if [ -d "$HOME/.config/alacritty" ] || command -v alacritty >/dev/null 2>&1; then
    link_file "$KW_ROOT/theme/alacritty.toml" "$HOME/.config/alacritty/alacritty.toml"
fi

# Kitty (se diretório ou binário existir)
if [ -d "$HOME/.config/kitty" ] || command -v kitty >/dev/null 2>&1; then
    link_file "$KW_ROOT/theme/kitty.conf" "$HOME/.config/kitty/kitty.conf"
fi

# btop tema
mkdir -p "$HOME/.config/btop/themes" 2>/dev/null || true
link_file "$KW_ROOT/theme/btop.theme" "$HOME/.config/btop/themes/killerwhale.theme"

# Universal Access CLI (kw e killerwhale)
mkdir -p "$HOME/.local/bin" 2>/dev/null || true
link_file "$KW_ROOT/kw" "$HOME/.local/bin/kw"
link_file "$KW_ROOT/launcher/killerwhale.sh" "$HOME/.local/bin/killerwhale"

# Tentativa de links globais no /usr/local/bin se houver sudo/root
if [ "$(id -u)" -eq 0 ]; then
    ln -sf "$KW_ROOT/kw" "/usr/local/bin/kw" 2>/dev/null || true
    ln -sf "$KW_ROOT/launcher/killerwhale.sh" "/usr/local/bin/killerwhale" 2>/dev/null || true
    log_ok "Comandos 'kw' e 'killerwhale' instalados em /usr/local/bin"
elif [ -n "$SUDO_CMD" ]; then
    $SUDO_CMD ln -sf "$KW_ROOT/kw" "/usr/local/bin/kw" 2>/dev/null || true
    $SUDO_CMD ln -sf "$KW_ROOT/launcher/killerwhale.sh" "/usr/local/bin/killerwhale" 2>/dev/null || true
    log_ok "Comandos 'kw' e 'killerwhale' instalados em /usr/local/bin"
fi

# Configuração de PATH e aliases no ~/.bashrc
if [ -f "$HOME/.bashrc" ] && ! grep -q "KILLERWHALE_ENV" "$HOME/.bashrc"; then
    cat << 'EOF' >> "$HOME/.bashrc"

# --- KILLERWHALE_ENV ---
export PATH="$HOME/.local/bin:$PATH"
alias kw="$HOME/.local/bin/kw"
alias killerwhale="$HOME/.local/bin/killerwhale"
# -----------------------
EOF
    log_ok "Ambiente e atalhos configurados em ~/.bashrc"
fi

# 7. Conclusão e Permissões
log_step "7/7. Ajustando permissões de execução dos scripts..."
if [ "$DRY_RUN" = true ]; then
    log_info "[DRY-RUN] Aplicaria chmod +x em scripts do projeto."
else
    chmod +x "$KW_ROOT/kw" 2>/dev/null || true
    chmod +x "$KW_ROOT/launcher/killerwhale.sh" 2>/dev/null || true
    chmod +x "$KW_ROOT/workspaces/00-dashboard/"*.sh
    chmod +x "$KW_ROOT/workspaces/01-recon/"*.sh 2>/dev/null || true
    chmod +x "$KW_ROOT/workspaces/02-exploit/"*.sh 2>/dev/null || true
    chmod +x "$KW_ROOT/launcher/"*.sh
    chmod +x "$KW_ROOT/wrappers/"*.py 2>/dev/null || true
    chmod +x "$KW_ROOT/tmux/"*.sh 2>/dev/null || true
    chmod +x "$KW_ROOT/theme/"*.sh 2>/dev/null || true
    log_ok "Permissões de execução ajustadas com sucesso."
fi


echo ""
echo -e "${KW_FG_BRIGHT}${KW_BOLD}========================================================================${KW_RESET}"
echo -e "${KW_FG_BRIGHT}${KW_BOLD}             INSTALAÇÃO DO KILLERWHALE FINALIZADA COM SUCESSO!          ${KW_RESET}"
echo -e "${KW_FG_BRIGHT}${KW_BOLD}========================================================================${KW_RESET}"
echo -e "${KW_FG_WHITE}Comandos universais disponíveis de qualquer diretório na VM:${KW_RESET}"
echo -e "  ${KW_FG_GREEN}kw${KW_RESET}          -> Inicia a interface TUI reativa v4 diretamente"
echo -e "  ${KW_FG_GREEN}killerwhale${KW_RESET} -> Inicia a estação de trabalho completa (tmux + workspaces + TUI)"
echo -e "  ${KW_FG_GREEN}kw session${KW_RESET}  -> Alternativa para iniciar a estação tmux"
echo ""

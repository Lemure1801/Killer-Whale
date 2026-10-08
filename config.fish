# KillerWhale — fish shell configuration
# Localizado no repositório e preparado para ser symlinkado em ~/.config/fish/config.fish

if status is-interactive
    # Determina o diretório raiz do KillerWhale se não definido (resolvendo symlinks)
    if not set -q KW_ROOT
        set -l script_path (status filename)
        if test -e "$script_path"
            set -gx KW_ROOT (path dirname (realpath "$script_path"))
        else if test -d "$HOME/KillerWhale"
            set -gx KW_ROOT "$HOME/KillerWhale"
        else
            set -gx KW_ROOT (status dirname)
        end
    end

    # Adiciona diretórios do KillerWhale ao PATH
    if test -d "$KW_ROOT/launcher"
        fish_add_path "$KW_ROOT/launcher"
    end
    if test -d "$KW_ROOT/wrappers"
        fish_add_path "$KW_ROOT/wrappers"
    end

    # Configuração de Logs
    set -q KW_LOG_DIR; or set -gx KW_LOG_DIR "$KW_ROOT/logs"

    # Atalhos rápidos do KillerWhale
    alias kw="$KW_ROOT/kw"
    alias killerwhale="$KW_ROOT/killerwhale"
    alias kw-session="$KW_ROOT/tmux/session.sh"
    alias kw-dash="$KW_ROOT/workspaces/00-dashboard/dashboard.sh"
    alias kw-clean="$KW_ROOT/workspaces/00-dashboard/cleanup.sh"
    alias kw-cheat="$KW_ROOT/workspaces/00-dashboard/cheatsheet.sh"
    alias kw-edit="XDG_CONFIG_HOME=$KW_ROOT nvim"

    # Exporta EDITOR como neovim
    set -gx EDITOR nvim
    set -gx VISUAL nvim
end

#!/usr/bin/env bash
# ==============================================================================
# KillerWhale — Launcher para o Neovim Isolado
# Garante isolamento de dotfiles apontando XDG_CONFIG_HOME para o projeto
# ==============================================================================
set -euo pipefail

KW_ROOT="${KW_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

if ! command -v nvim >/dev/null 2>&1; then
    echo "[✗] Neovim não encontrado no PATH. Instale com: sudo pacman -S neovim"
    exit 1
fi

export XDG_CONFIG_HOME="$KW_ROOT"
exec nvim "$@"

#!/usr/bin/env bash
# ==============================================================================
# KillerWhale — Universal Launcher CLI
# Inicia ou anexa à sessão tmux de trabalho ou TUI Textual de forma inteligente
# ==============================================================================
set -euo pipefail

# Resolução canônica do diretório raiz mesmo através de symlinks
SOURCE="${BASH_SOURCE[0]}"
while [ -L "$SOURCE" ]; do
    DIR="$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)"
    SOURCE="$(readlink "$SOURCE")"
    [[ "$SOURCE" != /* ]] && SOURCE="$DIR/$SOURCE"
done
KW_ROOT="$(cd -P "$(dirname "$SOURCE")/.." && pwd)"
export KW_ROOT

if [ "${1:-}" = "--tui" ] || [ "${1:-}" = "-t" ]; then
    shift
    exec "$KW_ROOT/kw" "$@"
fi

exec "$KW_ROOT/kw" session "$@"

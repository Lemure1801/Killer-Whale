#!/usr/bin/env bash
# ==============================================================================
# KillerWhale — Smoke Test de Sintaxe e Integridade Estrutural
# Valida scripts Bash, código Python, Lua, Fish e arquivos de configuração.
# Seguro para rodar no ambiente de desenvolvimento / sandbox (não altera o sistema).
# ==============================================================================
set -euo pipefail

KW_ROOT="${KW_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# shellcheck source=/dev/null
[ -f "$KW_ROOT/theme/colors.sh" ] && source "$KW_ROOT/theme/colors.sh"

PASSED=0
FAILED=0

test_check() {
    local desc="$1"
    local cmd="$2"
    echo -ne "  [TEST] $desc ... "
    if eval "$cmd" >/dev/null 2>&1; then
        echo -e "${KW_FG_BRIGHT}[PASS]${KW_RESET}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${KW_FG_ALERT}[FAIL]${KW_RESET}"
        FAILED=$((FAILED + 1))
    fi
}

echo -e "${KW_FG_GREEN}${KW_BOLD}"
cat << "EOF"
  _  ___ _ _     __          ___           _      
 | |/ (_) | |    \ \        / / |         | |     
 | ' / _| | | ___ \ \  /\  / /| |__   __ _| | ___ 
 |  < | | | |/ _ \ \ \/  \/ / | '_ \ / _` | |/ _ \
 | . \| | | |  __/  \  /\  /  | | | | (_| | |  __/
 |_|\_\_|_|_|\___|   \/  \/   |_| |_|\__,_|_|\___|
EOF
echo -e "${KW_FG_DIM}========================================================================${KW_RESET}"
echo -e "${KW_FG_BRIGHT}${KW_BOLD}           SUÍTE DE SMOKE TESTS // INTEGRIDADE DO PROJETO               ${KW_RESET}"
echo -e "${KW_FG_DIM}========================================================================${KW_RESET}\n"

echo -e "${KW_FG_GREEN}[1] Integridade Estrutural de Diretórios:${KW_RESET}"
test_check "Diretório bootstrap/" "[ -d '$KW_ROOT/bootstrap' ]"
test_check "Diretório tmux/" "[ -d '$KW_ROOT/tmux' ]"
test_check "Diretório workspaces/00-dashboard/" "[ -d '$KW_ROOT/workspaces/00-dashboard' ]"
test_check "Diretório workspaces/01-recon/" "[ -d '$KW_ROOT/workspaces/01-recon' ]"
test_check "Diretório workspaces/02-exploit/" "[ -d '$KW_ROOT/workspaces/02-exploit' ]"
test_check "Diretório launcher/" "[ -d '$KW_ROOT/launcher' ]"
test_check "Diretório wrappers/" "[ -d '$KW_ROOT/wrappers' ]"
test_check "Diretório killerwhale/ (Engine Textual)" "[ -d '$KW_ROOT/killerwhale' ]"
test_check "Diretório nvim/" "[ -d '$KW_ROOT/nvim' ]"
test_check "Diretório cheatsheets/" "[ -d '$KW_ROOT/cheatsheets' ]"
test_check "Diretório theme/" "[ -d '$KW_ROOT/theme' ]"
test_check "Diretório logs/" "[ -d '$KW_ROOT/logs' ]"
test_check "Executável kw (CLI de Entrada)" "[ -x '$KW_ROOT/kw' ]"

echo -e "\n${KW_FG_GREEN}[2] Validação de Sintaxe Bash (bash -n):${KW_RESET}"
while IFS= read -r script; do
    rel_path="${script#"$KW_ROOT/"}"
    test_check "Bash: $rel_path" "bash -n '$script'"
done < <(find "$KW_ROOT" -type f -name "*.sh")

echo -e "\n${KW_FG_GREEN}[3] Validação de Sintaxe Python (py_compile / AST):${KW_RESET}"
while IFS= read -r py_file; do
    rel_path="${py_file#"$KW_ROOT/"}"
    test_check "Python: $rel_path" "python3 -m py_compile '$py_file'"
done < <(find "$KW_ROOT/wrappers" "$KW_ROOT/killerwhale" -type f -name "*.py")
# Limpa caches temporários criados pelo py_compile
rm -rf "$KW_ROOT/wrappers/__pycache__" "$KW_ROOT/killerwhale/__pycache__" "$KW_ROOT/killerwhale/core/__pycache__" "$KW_ROOT/killerwhale/screens/__pycache__"


echo -e "\n${KW_FG_GREEN}[4] Validação de Sintaxe Lua (luac -p):${KW_RESET}"
if command -v luac >/dev/null 2>&1; then
    while IFS= read -r lua_file; do
        rel_path="${lua_file#"$KW_ROOT/"}"
        test_check "Lua: $rel_path" "luac -p '$lua_file'"
    done < <(find "$KW_ROOT/nvim" -type f -name "*.lua")
else
    echo "  [i] luac não disponível no host; teste ignorado."
fi

echo -e "\n${KW_FG_GREEN}[5] Validação de Sintaxe Fish (fish -n):${KW_RESET}"
if command -v fish >/dev/null 2>&1; then
    test_check "Fish: config.fish" "fish -n '$KW_ROOT/config.fish'"
else
    echo "  [i] fish não disponível no host; teste ignorado."
fi

echo -e "\n${KW_FG_GREEN}[6] Presença de Arquivos Chave de Configuração:${KW_RESET}"
test_check "README.md" "[ -s '$KW_ROOT/README.md' ]"
test_check ".gitignore" "[ -s '$KW_ROOT/.gitignore' ]"
test_check "logs/.gitkeep" "[ -f '$KW_ROOT/logs/.gitkeep' ]"
test_check "tmux.conf" "[ -s '$KW_ROOT/tmux/tmux.conf' ]"
test_check "colors.sh" "[ -s '$KW_ROOT/theme/colors.sh' ]"
test_check "alacritty.toml" "[ -s '$KW_ROOT/theme/alacritty.toml' ]"
test_check "kitty.conf" "[ -s '$KW_ROOT/theme/kitty.conf' ]"
test_check "btop.theme" "[ -s '$KW_ROOT/theme/btop.theme' ]"
test_check "nvim/init.lua" "[ -s '$KW_ROOT/nvim/init.lua' ]"
test_check "kw (CLI)" "[ -s '$KW_ROOT/kw' ]"
test_check "killerwhale.sh (Launcher)" "[ -s '$KW_ROOT/launcher/killerwhale.sh' ]"
test_check "requirements.txt" "[ -s '$KW_ROOT/requirements.txt' ]"

echo -e "\n${KW_FG_GREEN}[7] Validação Funcional da Engine Textual & Módulos (Python/Asyncio):${KW_RESET}"
PYTHON_TEST_BIN="$KW_ROOT/.venv/bin/python"
if [ ! -x "$PYTHON_TEST_BIN" ]; then
    PYTHON_TEST_BIN="python3"
fi

for test_script in "$KW_ROOT/tests"/test_etapa*.py "$KW_ROOT/tests"/test_marco_*.py "$KW_ROOT/tests"/test_cli_*.py; do
    if [ -f "$test_script" ]; then
        test_name="$(basename "$test_script")"
        test_check "Teste: $test_name" "PYTHONPATH='$KW_ROOT' '$PYTHON_TEST_BIN' '$test_script'"
    fi
done


echo -e "\n${KW_FG_DIM}========================================================================${KW_RESET}"
echo -e "${KW_FG_WHITE}Resultados: ${KW_FG_BRIGHT}${PASSED} passaram${KW_RESET}, ${KW_FG_ALERT}${FAILED} falharam${KW_RESET}."
echo -e "${KW_FG_DIM}========================================================================${KW_RESET}"

if [ "$FAILED" -eq 0 ]; then
    echo -e "${KW_FG_BRIGHT}[✓] Todos os smoke tests foram executados com sucesso!${KW_RESET}\n"
    exit 0
else
    echo -e "${KW_FG_ALERT}[✗] Falhas encontradas na validação.${KW_RESET}\n"
    exit 1
fi

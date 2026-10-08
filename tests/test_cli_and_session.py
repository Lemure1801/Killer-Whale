"""
Test CLI & Session Handling:
Verifies:
1. `kw` help and doctor subcommands return exit code 0.
2. Canonical resolution of `kw` and `launcher/killerwhale.sh` through symlinks.
3. `tmux/session.sh` handling when TMUX environment variable is set (no nesting crash).
"""

import os
import subprocess
import tempfile
from pathlib import Path

KW_ROOT = Path(__file__).resolve().parent.parent


def test_kw_cli_help():
    res = subprocess.run([str(KW_ROOT / "kw"), "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Uso: kw" in res.stdout
    assert "killerwhale" in res.stdout
    print("[✓] kw --help executado com sucesso.")


def test_kw_cli_doctor():
    res = subprocess.run([str(KW_ROOT / "kw"), "doctor"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Verificando ambiente KillerWhale" in res.stdout
    print("[✓] kw doctor executado com sucesso.")


def test_kw_symlink_resolution():
    with tempfile.TemporaryDirectory() as tmpdir:
        symlink_kw = Path(tmpdir) / "kw"
        symlink_kw.symlink_to(KW_ROOT / "kw")

        res = subprocess.run([str(symlink_kw), "--help"], capture_output=True, text=True)
        assert res.returncode == 0
        assert "Uso: kw" in res.stdout
        print("[✓] Resolução canônica de symlink para kw validada.")


def test_session_nested_guard():
    # Simulate being inside an active tmux environment with TMUX set
    env = os.environ.copy()
    env["TMUX"] = "/tmp/tmux-mock,99999,0"
    res = subprocess.run(
        ["bash", str(KW_ROOT / "tmux" / "session.sh")],
        env=env,
        capture_output=True,
        text=True,
    )
    combined = res.stdout + res.stderr
    assert "sessions should be nested with care" not in combined
    print("[✓] Proteção contra erro de sessões aninhadas ($TMUX) confirmada.")


def test_requirements_file():
    req_file = KW_ROOT / "requirements.txt"
    assert req_file.is_file()
    content = req_file.read_text()
    assert "textual" in content
    assert "pynvim" in content
    assert "psutil" in content
    print("[✓] requirements.txt verificado com sucesso.")


if __name__ == "__main__":
    test_requirements_file()
    test_kw_cli_help()
    test_kw_cli_doctor()
    test_kw_symlink_resolution()
    test_session_nested_guard()
    print("[✓] Todos os testes de CLI e Sessão passaram com sucesso!")

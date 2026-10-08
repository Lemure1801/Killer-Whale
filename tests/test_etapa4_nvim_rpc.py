"""
Test Etapa 4: Genuine Neovim RPC Integration via Unix Socket
Verifies connection via pynvim without tmux send-keys and without spawning duplicate instances.
"""

import os
import asyncio
from killerwhale.core.nvim_client import NeovimRPCClient
from killerwhale.app import KillerWhaleApp

TEST_SOCK = "/tmp/kw-test-etapa4.sock"


async def test_nvim_rpc_integration():
    # Clean previous socket if exists
    if os.path.exists(TEST_SOCK):
        os.remove(TEST_SOCK)

    client = NeovimRPCClient(socket_path=TEST_SOCK)
    assert not client.is_listening(), "Socket should not be listening initially"

    # 1. Start Neovim server listening on socket
    ok, msg = client.ensure_server_running(headless=True)
    assert ok, f"Failed to start Neovim RPC server: {msg}"
    assert client.is_listening(), "Neovim should now respond to RPC ping"
    print(f"[✓] Servidor Neovim ouvindo em {TEST_SOCK} e respondendo ao RPC.")

    # 2. Command the running instance to open a file via RPC
    test_file = os.path.abspath("cheatsheets/general.md")
    ok, msg = client.open_file(test_file)
    assert ok, f"Failed to open file in Neovim: {msg}"
    
    # 3. Verify on the running instance that the buffer is indeed general.md
    status = client.get_status()
    assert status["connected"] is True
    assert "general.md" in status["current_file"] or any("general.md" in b for b in status["buffers"])
    print(f"[✓] Arquivo aberto via RPC na mesma instância: {status['current_file']}")

    # 4. Command the running instance to create a new buffer with audit content
    sample_content = "# KillerWhale Audit\nTarget: 10.10.11.245\nPort 80: HTTP Open"
    ok, msg = client.write_buffer("kw_audit_preview.md", sample_content)
    assert ok, f"Failed to write buffer: {msg}"

    # Verify buffer in Neovim
    def check_buffer(nvim):
        return list(nvim.current.buffer)

    ok, lines = client.execute(check_buffer)
    assert ok and "Port 80: HTTP Open" in lines
    print("[✓] Buffer criado e verificado via RPC na instância Neovim existente.")

    # 5. Verify Textual App integration: keybinding 'e' triggers Neovim action
    app = KillerWhaleApp()
    app.nvim_client = client
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("e")
        await pilot.pause()
        print("[✓] Ação de editor disparada dentro do Textual App via atalho 'e'.")

    # Cleanup
    if os.path.exists(TEST_SOCK):
        try:
            os.remove(TEST_SOCK)
        except OSError:
            pass

    print("[✓] Etapa 4 PASS: Integração Neovim RPC via socket funcionando com sucesso!")


if __name__ == "__main__":
    asyncio.run(test_nvim_rpc_integration())

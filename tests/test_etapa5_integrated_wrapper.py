"""
Test Etapa 5: Integrated Wrapper Execution & End-to-End Neovim Delivery
Verifies running the Nmap audit wrapper from the Textual interface,
extracting findings to the DataTable, saving the log, and opening it in Neovim via RPC.
"""

import os
import asyncio
from killerwhale.app import KillerWhaleApp
from killerwhale.screens.scanner import ScannerScreen
from killerwhale.core.nvim_client import NeovimRPCClient
from killerwhale.core.orchestrator import execute_nmap_scan, parse_nmap_ports

TEST_SOCK = "/tmp/kw-test-etapa5.sock"


async def test_integrated_wrapper_flow():
    if os.path.exists(TEST_SOCK):
        os.remove(TEST_SOCK)

    # 1. Start dedicated Neovim RPC server for this test
    nvim_client = NeovimRPCClient(socket_path=TEST_SOCK)
    ok, msg = nvim_client.ensure_server_running(headless=True)
    assert ok, f"Neovim server failed to start: {msg}"
    print(f"[✓] Servidor Neovim RPC ativo em {TEST_SOCK}")

    # 2. Launch Textual app with our Neovim client configured
    app = KillerWhaleApp(legacy=True)
    app.nvim_client = nvim_client


    async with app.run_test() as pilot:
        await pilot.pause()

        # Navigate to Recon Scanner screen via shortcut '1' from dashboard
        await pilot.press("1")
        await pilot.pause()
        assert isinstance(app.screen, ScannerScreen), f"Expected ScannerScreen, got {type(app.screen)}"
        scanner = app.screen
        assert scanner.tool_type == "recon"
        print("[✓] Navegação para Recon Scanner (Workspace 01) confirmada.")

        # 3. Configure target and run scan via clicking run button
        scanner.input_target.value = "10.10.11.245"
        await pilot.click("#btn-run")
        await pilot.pause()

        # 4. Verify scan execution and DataTable population
        assert scanner.last_result is not None, "Last result should be populated"
        res = scanner.last_result
        assert res.return_code == 0
        assert os.path.isfile(res.log_path), f"Audit log file must exist at {res.log_path}"
        assert len(res.ports) > 0, "Discovered ports should be parsed"
        assert scanner.table_findings.row_count > 0, "DataTable rows should be populated"
        print(f"[✓] Varredura executada: {len(res.ports)} portas identificadas. Log salvo em: {res.log_path}")

        # 5. Verify 'Abrir no Neovim' button enabled and trigger action via click
        btn_nvim = scanner.query_one("#btn-open-nvim")
        assert not btn_nvim.disabled, "Button should be enabled after scan"
        await pilot.click("#btn-open-nvim")
        await pilot.pause(0.5)

        # 6. Verify via Neovim RPC that the exact log file is open in Neovim's buffer
        status = nvim_client.get_status()
        assert status["connected"] is True
        log_basename = os.path.basename(res.log_path)
        assert log_basename in status["current_file"] or any(log_basename in b for b in status["buffers"]), \
            f"Expected {log_basename} in Neovim buffers, got current: {status['current_file']}, buffers: {status['buffers']}"
        print(f"[✓] Fluxo end-to-end verificado: Log '{log_basename}' aberto no buffer do Neovim via RPC!")

    # Cleanup
    if os.path.exists(TEST_SOCK):
        try:
            os.remove(TEST_SOCK)
        except OSError:
            pass

    print("[✓] Etapa 5 PASS: Wrapper integrado rodando na interface e abrindo no Neovim end-to-end com sucesso!")


if __name__ == "__main__":
    asyncio.run(test_integrated_wrapper_flow())

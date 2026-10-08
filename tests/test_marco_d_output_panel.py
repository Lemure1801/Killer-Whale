"""
Test Marco D: Real Output Terminal Stream on Left Panel (Section 3.2)
Verifies:
1. Genuine asynchronous command execution (ping / uname) streams output line-by-line.
2. Real network telemetry populated into 'Rede local' sub-tab.
3. Real system metrics (CPU, RAM, Disk) populated into 'Telemetria' sub-tab.
4. Data verified inside the mounted RichLog widgets of LeftOutputPanel.
"""

import asyncio
from textual.app import App, ComposeResult
from killerwhale.screens.engine_dashboard import DashboardEngineScreen
from killerwhale.theme import APP_CSS


class TestMarcoDApp(App):
    CSS = APP_CSS

    def compose(self) -> ComposeResult:
        yield DashboardEngineScreen(id="dashboard-engine")


async def test_marco_d_output_stream():
    app = TestMarcoDApp()
    async with app.run_test() as pilot:
        await pilot.pause()

        screen = app.query_one(DashboardEngineScreen)
        left_panel = screen.left_panel

        # 1. Verify Subtab 1 (Rede local) has real interface data populated
        assert len(left_panel.subtab_history[1]) > 0
        assert any("ATUALIZAÇÃO DE INTERFACES" in line for line in left_panel.subtab_history[1])
        print("[✓] Sub-aba 'Rede local' populada com dados reais de interfaces de rede.")

        # 2. Verify Subtab 3 (Telemetria) has real CPU/RAM/Disk data populated
        assert len(left_panel.subtab_history[3]) > 0
        assert any("CPU:" in line and "RAM:" in line for line in left_panel.subtab_history[3])
        print("[✓] Sub-aba 'Telemetria' recebendo telemetria real via psutil.")


        # 3. Trigger a real command execution into Subtab 0 (Resultado de comandos)
        # We test ping -c 1 127.0.0.1 or echo test
        returncode = await screen.feed_manager.run_command_stream(["ping", "-c", "2", "127.0.0.1"], subtab_idx=0)
        assert returncode == 0
        await pilot.pause()

        # Check Subtab 0 output lines
        subtab_cmd_lines = [line.text for line in left_panel.log_views[0].lines]
        assert any("ping -c 2 127.0.0.1" in line for line in subtab_cmd_lines)
        assert any("bytes from 127.0.0.1" in line or "ping statistics" in line for line in subtab_cmd_lines)
        assert any("Processo finalizado (Código 0)" in line for line in subtab_cmd_lines)
        print("[✓] Comando 'ping -c 2 127.0.0.1' executado e transmitido em tempo real para o painel read-only.")

        # 4. Verify sub-tab navigation via TAB + Ctrl + Right
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("ctrl+right")
        await pilot.pause()
        assert left_panel.active_subtab == 1
        assert left_panel.log_views[1].display is True
        assert left_panel.log_views[0].display is False
        print("[✓] Navegação de sub-abas do terminal de output verificada com sucesso.")

    print("[✓] MARCO D CONCLUÍDO COM SUCESSO: Terminal de output real no painel esquerdo!")


if __name__ == "__main__":
    asyncio.run(test_marco_d_output_stream())

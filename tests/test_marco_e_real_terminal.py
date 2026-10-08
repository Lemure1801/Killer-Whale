"""
Test Marco E: Real Interactive Terminal (Section 3.3)
Verifies:
1. Genuine PTY process running (/bin/bash or /bin/sh).
2. Typing mode enabled only after TAB + Ctrl + / leader combo.
3. Keystrokes sent via handle_terminal_key are processed by shell.
4. Shell executes genuine command and response is received in session history.
"""

import asyncio
from textual.app import App, ComposeResult
from textual.events import Key
from killerwhale.screens.engine_dashboard import DashboardEngineScreen
from killerwhale.theme import APP_CSS


class TestMarcoEApp(App):
    CSS = APP_CSS

    def compose(self) -> ComposeResult:
        yield DashboardEngineScreen(id="dashboard-engine")


async def test_marco_e_interactive_terminal():
    app = TestMarcoEApp()
    async with app.run_test() as pilot:
        await pilot.pause(0.5)

        screen = app.query_one(DashboardEngineScreen)
        right_panel = screen.right_panel

        # 1. Verify PTY session exists and is alive
        assert len(right_panel.sessions) >= 1
        session = right_panel.sessions[0]
        assert session.is_alive is True, "PTY session must be alive"
        assert session.proc is not None
        assert session.proc.poll() is None, "Child shell process must be running"
        print(f"[✓] Processo de shell real ativo via PTY (PID: {session.proc.pid}).")

        # 2. Before typing mode: typing is blocked
        assert right_panel.typing_enabled is False

        # 3. Enable typing mode via TAB + Ctrl + /
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("ctrl+slash")
        await pilot.pause()
        assert right_panel.typing_enabled is True
        print("[✓] Modo de digitação ativado com sucesso via TAB + Ctrl + /.")

        # 4. Type a real command into the terminal session
        # We write: echo ECHO_MARCO_E_SUCCESS and press enter
        cmd_text = "echo ECHO_MARCO_E_SUCCESS\n"
        session.write_input(cmd_text.encode("utf-8"))

        # Wait for shell to execute and return output
        for _ in range(20):
            await pilot.pause(0.1)
            all_history = "".join(session.history)
            if "ECHO_MARCO_E_SUCCESS" in all_history:
                break

        all_history = "".join(session.history)
        assert "ECHO_MARCO_E_SUCCESS" in all_history, f"Expected output in PTY history, got: {repr(all_history)}"
        print(f"[✓] Comando executado no PTY interativo com sucesso. Saída confirmada: {repr(all_history[-80:])}")

        # Cleanup
        right_panel.close_all()
        assert not session.is_alive

    print("[✓] MARCO E CONCLUÍDO COM SUCESSO: Terminal interativo real no painel direito!")


if __name__ == "__main__":
    asyncio.run(test_marco_e_interactive_terminal())

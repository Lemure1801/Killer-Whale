"""
Test Marco F: Multiple Simultaneous Terminals & Lifecycle Management
Verifies:
1. Multiple interactive terminals opened as sub-tabs via TAB + Ctrl + T.
2. Distinct parallel real shell processes (distinct PIDs) running simultaneously.
3. Independent I/O handling on each parallel terminal.
4. Individual terminal closure via TAB + Ctrl + W without orphan processes.
"""

import os
import asyncio
from textual.app import App, ComposeResult
from killerwhale.screens.engine_dashboard import DashboardEngineScreen
from killerwhale.theme import APP_CSS


class TestMarcoFApp(App):
    CSS = APP_CSS

    def compose(self) -> ComposeResult:
        yield DashboardEngineScreen(id="dashboard-engine")


async def test_marco_f_multiple_terminals():
    app = TestMarcoFApp()
    async with app.run_test() as pilot:
        await pilot.pause(0.5)

        screen = app.query_one(DashboardEngineScreen)
        right_panel = screen.right_panel

        # 1. Initial terminal 1
        assert len(right_panel.sessions) == 1
        session1 = right_panel.sessions[0]
        pid1 = session1.proc.pid
        assert session1.is_alive is True
        print(f"[✓] Terminal 1 inicial ativo com PID {pid1}.")

        # 2. Open Terminal 2 via TAB + Ctrl + T
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("ctrl+t")
        await pilot.pause(0.5)

        assert len(right_panel.sessions) == 2
        assert len(right_panel.terminal_titles) == 2
        session2 = right_panel.sessions[1]
        pid2 = session2.proc.pid
        assert session2.is_alive is True
        assert pid1 != pid2, "Each terminal session must run a distinct parallel process"
        print(f"[✓] Terminal 2 aberto via TAB + Ctrl + T com PID {pid2} (Paralelo ao Terminal 1).")

        # 3. Send commands to both terminals in parallel
        session1.write_input(b"echo T1_PARALLEL_EXEC\n")
        session2.write_input(b"echo T2_PARALLEL_EXEC\n")

        # Await responses on both PTYs
        for _ in range(25):
            await pilot.pause(0.1)
            h1 = "".join(session1.history)
            h2 = "".join(session2.history)
            if "T1_PARALLEL_EXEC" in h1 and "T2_PARALLEL_EXEC" in h2:
                break

        h1 = "".join(session1.history)
        h2 = "".join(session2.history)
        assert "T1_PARALLEL_EXEC" in h1, "Terminal 1 should have received its own command output"
        assert "T2_PARALLEL_EXEC" in h2, "Terminal 2 should have received its own command output"
        print("[✓] Processos paralelos executaram comandos independentes em simultâneo com sucesso.")

        # 4. Close current terminal (Terminal 2) via TAB + Ctrl + W
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("ctrl+w")
        await pilot.pause(0.5)

        # Verify Terminal 2 was removed
        assert len(right_panel.sessions) == 1
        assert len(right_panel.terminal_titles) == 1
        assert right_panel.terminal_titles[0] == "Terminal 1"

        # Verify session2 process is terminated (no orphan process)
        assert not session2.is_alive, "Closed session must not be alive"
        session2_exit = session2.proc.poll()
        assert session2_exit is not None, f"Closed terminal process {pid2} must have terminated, poll={session2_exit}"
        print(f"[✓] Terminal 2 (PID {pid2}) encerrado com código {session2_exit} sem deixar processo órfão.")

        # Verify Terminal 1 is still alive and operational
        assert session1.is_alive is True
        assert session1.proc.poll() is None
        print("[✓] Terminal 1 permaneceu ativo e operacional após o fechamento do Terminal 2.")

        # Cleanup all
        right_panel.close_all()

    print("[✓] MARCO F CONCLUÍDO COM SUCESSO: Múltiplos terminais simultâneos e ciclo de vida limpo!")


if __name__ == "__main__":
    asyncio.run(test_marco_f_multiple_terminals())

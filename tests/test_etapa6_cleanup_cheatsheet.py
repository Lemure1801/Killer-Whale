"""
Test Etapa 6: Integrated Cleanup and Cheatsheet Screens
Verifies porting of cleanup.sh and cheatsheet.sh into Textual with Markdown rendering
and system maintenance execution.
"""

import asyncio
from killerwhale.app import KillerWhaleApp
from killerwhale.screens.cleanup import CleanupScreen
from killerwhale.screens.cheatsheet import CheatsheetScreen
from killerwhale.screens.dashboard import DashboardScreen
from killerwhale.core.cleanup import run_cleanup_task, CLEANUP_TASKS


async def test_cleanup_and_cheatsheet():
    # 1. Direct core test of cleanup tasks
    assert len(CLEANUP_TASKS) == 6
    ok, msg = run_cleanup_task("kw_logs")
    assert ok is True
    print(f"[✓] Execução de tarefa de cleanup (core): {msg}")

    app = KillerWhaleApp(legacy=True)
    async with app.run_test() as pilot:

        await pilot.pause()

        # 2. Test navigation to CleanupScreen via shortcut 'c'
        await pilot.press("c")
        await pilot.pause()
        assert isinstance(app.screen, CleanupScreen), f"Expected CleanupScreen, got {type(app.screen)}"
        cleanup = app.screen
        print("[✓] Navegação para CleanupScreen confirmada.")

        # Test running a task via screen button
        await pilot.click("#btn-run-sel")
        await pilot.pause()
        assert len(cleanup.log_view.lines) > 0, "Log should contain execution output"
        print("[✓] Execução de tarefa de limpeza na interface confirmada.")

        # Return to Dashboard via ESC
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, DashboardScreen)

        # 3. Test navigation to CheatsheetScreen via shortcut 'h'
        await pilot.press("h")
        await pilot.pause()
        assert isinstance(app.screen, CheatsheetScreen), f"Expected CheatsheetScreen, got {type(app.screen)}"
        cheats = app.screen
        assert len(cheats.cheatsheets) >= 4, f"Expected at least 4 cheatsheets, found {len(cheats.cheatsheets)}"
        names = [name for name, _ in cheats.cheatsheets]
        assert "general.md" in names
        assert "nmap.md" in names
        assert "sqlmap.md" in names
        assert "recon.md" in names
        print(f"[✓] Cheatsheets descobertos e carregados: {', '.join(names)}")

        # Test filtering
        cheats.filter_input.value = "nmap"
        await pilot.pause()
        assert len(cheats.filtered_cheats) == 1
        assert cheats.filtered_cheats[0][0] == "nmap.md"
        assert cheats.current_file.endswith("nmap.md")
        print("[✓] Filtragem e renderização reativa de cheatsheet confirmadas.")

        # Return to Dashboard via ESC
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, DashboardScreen)
        print("[✓] Retorno ao Dashboard preservando estado confirmado.")

    print("[✓] Etapa 6 PASS: Cleanup e Cheatsheet integrados e funcionais dentro da aplicação Textual!")


if __name__ == "__main__":
    asyncio.run(test_cleanup_and_cheatsheet())

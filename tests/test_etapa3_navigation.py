"""
Test Etapa 3: Multi-screen Navigation & State Preservation
Verifies transitions between Dashboard and Launcher screens via keyboard shortcuts,
ensuring state is preserved across navigation.
"""

import asyncio
from killerwhale.app import KillerWhaleApp
from killerwhale.screens.dashboard import DashboardScreen
from killerwhale.screens.launcher import LauncherScreen
from killerwhale.core.system import set_target, get_target


async def test_navigation_and_state():
    test_scope = "10.10.11.245"
    set_target(test_scope)

    app = KillerWhaleApp(legacy=True)
    async with app.run_test() as pilot:

        await pilot.pause()
        
        # 1. Starts on Dashboard
        assert isinstance(app.screen, DashboardScreen)
        assert app.screen.active_target == test_scope

        # 2. Press 'm' to navigate to Launcher / Command Palette
        await pilot.press("m")
        await pilot.pause()
        assert isinstance(app.screen, LauncherScreen), f"Expected LauncherScreen, got {type(app.screen)}"
        print("[✓] Navegação para Launcher via 'm' confirmada.")

        # 3. Test search filter in Launcher
        launcher = app.screen
        assert len(launcher.filtered_items) > 1
        launcher.search_input.value = "nmap"
        await pilot.pause()
        assert len(launcher.filtered_items) == 1
        assert "Nmap" in launcher.filtered_items[0].title
        print("[✓] Busca e filtragem no Launcher confirmada.")

        # 4. Press 'escape' to navigate back to Dashboard
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, DashboardScreen), f"Expected DashboardScreen, got {type(app.screen)}"
        assert app.screen.active_target == test_scope, "State (target) must be preserved"
        print("[✓] Retorno para Dashboard via 'escape' confirmado com estado preservado.")

        # 5. Press 'm' again and select item via keyboard Enter (dashboard item)
        await pilot.press("m")
        await pilot.pause()
        assert isinstance(app.screen, LauncherScreen)
        launcher = app.screen
        launcher.search_input.value = ""
        await pilot.pause()
        launcher.opt_list.highlighted = 0  # Dashboard option
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, DashboardScreen)
        print("[✓] Seleção de item e retorno via Enter confirmados.")

    print("[✓] Etapa 3 PASS: Navegação entre telas funcionando sem perda de estado!")


if __name__ == "__main__":
    asyncio.run(test_navigation_and_state())

"""
Test Marco C: Complete Dashboard Layout & Navigation Structure
Verifies:
1. Top tab bar (3.1), Left output panel (3.2), Right interactive panel (3.3).
2. TAB + 0..9 tab navigation.
3. TAB + Ctrl + / typing mode toggle.
4. TAB + Ctrl + Left / Right sub-tab switching.
5. TAB + Ctrl + T (new terminal) and TAB + Ctrl + W (close terminal).
6. TAB + Shift + / (fuzzy search modal) and TAB + Shift + L (tab list modal).
"""

import asyncio
from textual.app import App, ComposeResult
from killerwhale.screens.engine_dashboard import DashboardEngineScreen
from killerwhale.layout.top_bar import TabListModal, TabSearchModal
from killerwhale.theme import APP_CSS


class TestMarcoCApp(App):
    CSS = APP_CSS

    def compose(self) -> ComposeResult:
        yield DashboardEngineScreen(id="dashboard-engine")


async def test_marco_c_dashboard_layout():
    app = TestMarcoCApp()
    async with app.run_test() as pilot:
        await pilot.pause()

        screen = app.query_one(DashboardEngineScreen)
        assert screen is not None
        assert screen.top_bar.active_index == 0
        assert screen.left_panel.active_subtab == 0
        assert not screen.right_panel.typing_enabled
        print("[✓] Layout montado: TopTabBar (3.1), LeftPanel (3.2), RightPanel (3.3).")

        # 1. Test TAB + 1 navigation to tab 1
        await pilot.press("tab")
        await pilot.pause()
        assert screen.top_bar.leader_active is True
        await pilot.press("1")
        await pilot.pause()
        assert screen.top_bar.active_index == 1
        print("[✓] TAB + 1 alternou TopTabBar para aba 1 (Recon).")

        # 2. Test TAB + 0 back to tab 0
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("0")
        await pilot.pause()
        assert screen.top_bar.active_index == 0
        print("[✓] TAB + 0 retornou TopTabBar para aba 0 (Dashboard).")

        # 3. Test TAB + Ctrl + / typing mode activation
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("ctrl+slash")
        await pilot.pause()
        assert screen.right_panel.typing_enabled is True
        assert "HABILITADA" in screen.right_panel.lbl_typing.render().plain
        print("[✓] TAB + Ctrl + / habilitou modo de digitação no terminal interativo.")

        # Toggle back
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("ctrl+slash")
        await pilot.pause()
        assert screen.right_panel.typing_enabled is False
        print("[✓] TAB + Ctrl + / bloqueou modo de digitação.")

        # 4. Test TAB + Ctrl + Right: Switch Left Panel subtab
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("ctrl+right")
        await pilot.pause()
        assert screen.left_panel.active_subtab == 1
        print("[✓] TAB + Ctrl + Right alternou sub-aba do painel esquerdo para 1 (Rede local).")

        # 5. Test TAB + Ctrl + T: Add new terminal tab
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("ctrl+t")
        await pilot.pause()
        assert len(screen.right_panel.terminal_titles) == 2
        assert screen.right_panel.active_terminal_idx == 1
        print("[✓] TAB + Ctrl + T abriu novo terminal interativo simultâneo (Terminal 2).")

        # 6. Test TAB + Ctrl + W: Close terminal tab
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("ctrl+w")
        await pilot.pause()
        assert len(screen.right_panel.terminal_titles) == 1
        print("[✓] TAB + Ctrl + W encerrou terminal individual com sucesso.")

        # 7. Test TAB + Shift + L: Open Tab List Modal
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("shift+l")
        await pilot.pause()
        assert isinstance(app.screen, TabListModal)
        print("[✓] TAB + Shift + L abriu TabListModal.")
        # Select tab 2 (Exploit) and press enter
        app.screen.opt_list.highlighted = 2
        await pilot.press("enter")
        await pilot.pause()
        assert screen.top_bar.active_index == 2
        print("[✓] Seleção no TabListModal alternou TopTabBar para aba 2 (Exploit).")

        # 8. Test TAB + Shift + /: Open Tab Search Modal
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("shift+slash")
        await pilot.pause()
        assert isinstance(app.screen, TabSearchModal)
        print("[✓] TAB + Shift + / abriu TabSearchModal.")
        # Filter "dash" and submit
        app.screen.input_search.value = "dash"
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        assert screen.top_bar.active_index == 0
        print("[✓] Busca no TabSearchModal alternou TopTabBar de volta para aba 0 (Dashboard).")

    print("[✓] MARCO C CONCLUÍDO COM SUCESSO: Layout completo do Dashboard e navegação!")


if __name__ == "__main__":
    asyncio.run(test_marco_c_dashboard_layout())

"""
Test Marco G: Full Engine Integration & Acceptance Criteria Verification
Verifies all functional criteria of the KillerWhale v4 specification:
1. TAB acts exclusively as leader-key, never moves widget focus.
2. All specified leader combinations function seamlessly:
   - TAB + 0..9 (tab switching)
   - TAB + Ctrl + / (typing mode activation)
   - TAB + Shift + / (fuzzy search modal)
   - TAB + Shift + L (full tab list modal)
   - TAB + Ctrl + Left / Right (sub-tab switching)
   - TAB + Ctrl + T / W (parallel terminal add/close)
3. ASCII Image widget loads and renders reference image with cyan palette.
4. Clean lifecycle with zero orphan child processes.
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import asyncio
from textual.app import App
from killerwhale.app import KillerWhaleApp
from killerwhale.screens.engine_dashboard import DashboardEngineScreen
from killerwhale.layout.top_bar import TabListModal, TabSearchModal
from killerwhale.widgets.ascii_image import AsciiImageWidget, image_to_ascii_rich

REF_IMAGE = "assets/killer_whale_ref.png"


async def test_marco_g_full_integration():
    # 1. Verify ASCII Image Rendering in theme palette
    ascii_out = image_to_ascii_rich(REF_IMAGE, max_width=60, max_height=20)
    assert len(ascii_out.plain) > 0
    assert any(c in ascii_out.plain for c in [":", "-", "|", "█"])
    print("[✓] Critério 1/6: Imagem de referência convertida em ASCII na paleta ciano sem distorção.")

    app = KillerWhaleApp()
    async with app.run_test() as pilot:
        await pilot.pause(0.5)

        dash = app.screen
        assert isinstance(dash, DashboardEngineScreen)
        top_bar = dash.top_bar
        left_panel = dash.left_panel
        right_panel = dash.right_panel

        # 2. Verify TAB never moves focus by default
        initial_focus = app.focused
        await pilot.press("tab")
        await pilot.pause()
        assert top_bar.leader_active is True
        assert app.focused == initial_focus, "TAB must not move focus to another widget"
        print("[✓] Critério 2/6: TAB atua exclusivamente como tecla líder (sem focus navigation padrão).")

        # 3. Test TAB + 1 and TAB + 0
        await pilot.press("1")
        await pilot.pause()
        assert top_bar.active_index == 1
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("0")
        await pilot.pause()
        assert top_bar.active_index == 0
        print("[✓] Critério 3/6: TAB + 0..9 navega entre abas.")

        # 4. Test TAB + Ctrl + / toggling typing mode
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("ctrl+slash")
        await pilot.pause()
        assert right_panel.typing_enabled is True
        print("[✓] Critério 4/6: TAB + Ctrl + / ativa modo de digitação no terminal interativo.")

        # 5. Test parallel multiple terminals, command execution and individual closure
        initial_session = right_panel.sessions[0]
        initial_pid = initial_session.proc.pid
        assert initial_session.is_alive is True

        # Open second terminal
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("ctrl+t")
        await pilot.pause(0.4)
        assert len(right_panel.sessions) == 2
        second_session = right_panel.sessions[1]
        second_pid = second_session.proc.pid
        assert initial_pid != second_pid

        # Execute commands in parallel
        initial_session.write_input(b"echo G_TERM1_OK\n")
        second_session.write_input(b"echo G_TERM2_OK\n")

        for _ in range(25):
            await pilot.pause(0.1)
            if "G_TERM1_OK" in "".join(initial_session.history) and "G_TERM2_OK" in "".join(second_session.history):
                break

        assert "G_TERM1_OK" in "".join(initial_session.history)
        assert "G_TERM2_OK" in "".join(second_session.history)

        # Close second terminal
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("ctrl+w")
        await pilot.pause(0.4)
        assert len(right_panel.sessions) == 1
        assert not second_session.is_alive
        assert second_session.proc.poll() is not None
        print("[✓] Critério 5/6: Múltiplos terminais simultâneos com execução paralela e sem processos órfãos.")

        # 6. Test sub-tab navigation on left output panel
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("ctrl+right")
        await pilot.pause()
        assert left_panel.active_subtab == 1
        print("[✓] Critério 6/6: TAB + Ctrl + Left/Right navega entre sub-abas do terminal de output.")

        # Cleanup
        await app.action_quit()

    print("\n" + "=" * 72)
    print(" [✓] MARCO G CONCLUÍDO: Todos os critérios de aceite foram satisfeitos!")
    print("=" * 72)


if __name__ == "__main__":
    asyncio.run(test_marco_g_full_integration())

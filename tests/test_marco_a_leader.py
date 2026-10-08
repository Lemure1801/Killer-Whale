"""
Test Marco A: Leader Key Engine in Isolation
Verifies:
1. TAB activates leader mode and prevents default focus movement.
2. TAB + 0 / TAB + 1 switches between tabs/screens.
3. Inactivity timeout (~1.5s) automatically clears leader mode.
"""

import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Label, Button, Static
from textual.containers import Vertical
from textual.events import Key

from killerwhale.core.leader import LeaderKeyManager
from killerwhale.theme import APP_CSS


class TestMarcoAApp(App):
    CSS = APP_CSS

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_tab = 0
        self.leader = LeaderKeyManager(timeout=1.0, on_state_change=self._on_leader_change)
        self.leader.register_digit_action(self._on_digit_action)

    def compose(self) -> ComposeResult:
        with Vertical(classes="box-panel"):
            self.lbl_leader = Label("[MODO NORMAL]", id="lbl-leader")
            self.lbl_screen = Label("TELA ATUAL: 0", id="lbl-screen")
            self.btn1 = Button("Botão 1 (Foco Inicial)", id="btn-1")
            self.btn2 = Button("Botão 2", id="btn-2")
            yield self.lbl_leader
            yield self.lbl_screen
            yield self.btn1
            yield self.btn2

    def on_mount(self) -> None:
        self.btn1.focus()
        # Regularly check leader timeout
        self.set_interval(0.1, self.leader.check_timeout)

    def _on_leader_change(self, is_active: bool) -> None:
        if is_active:
            self.lbl_leader.update("[LEADER: TAB ATIVO]")
        else:
            self.lbl_leader.update("[MODO NORMAL]")

    def _on_digit_action(self, digit: int) -> None:
        self.current_tab = digit
        self.lbl_screen.update(f"TELA ATUAL: {digit}")

    def on_key(self, event: Key) -> None:
        # Leader manager intercepts TAB and the following key
        handled = self.leader.handle_key(event)
        if handled:
            return


async def test_marco_a_leader():
    app = TestMarcoAApp()
    async with app.run_test() as pilot:
        await pilot.pause()

        # Initial state: focus on btn1, current_tab = 0, leader inactive
        assert app.focused == app.btn1
        assert app.current_tab == 0
        assert not app.leader.is_active

        # 1. Press TAB -> Leader mode engages, focus does NOT move to btn2
        await pilot.press("tab")
        await pilot.pause()
        assert app.leader.is_active, "Leader mode must be active after TAB"
        assert app.focused == app.btn1, "TAB must NOT move focus to btn2"
        print("[✓] Pressionar TAB ativou o modo líder sem mover foco dos widgets.")

        # 2. Press '1' while leader active -> switches current_tab to 1
        await pilot.press("1")
        await pilot.pause()
        assert not app.leader.is_active, "Leader mode must deactivate after chord completes"
        assert app.current_tab == 1, "TAB + 1 must switch to tab 1"
        print("[✓] TAB + 1 alternou com sucesso para a Tela 1.")

        # 3. Press TAB then '0' -> switches back to 0
        await pilot.press("tab")
        await pilot.pause()
        assert app.leader.is_active
        await pilot.press("0")
        await pilot.pause()
        assert app.current_tab == 0
        print("[✓] TAB + 0 alternou com sucesso para a Tela 0.")

        # 4. Test Timeout: Press TAB and wait without pressing another key
        await pilot.press("tab")
        await pilot.pause()
        assert app.leader.is_active
        # Wait > timeout (1.0s)
        await pilot.pause(1.2)
        assert not app.leader.is_active, "Leader mode must automatically expire after timeout"
        print("[✓] Timeout do modo líder (~1.0s) verificado com sucesso.")

    print("[✓] MARCO A CONCLUÍDO COM SUCESSO: Leader-key funcionando isoladamente!")


if __name__ == "__main__":
    asyncio.run(test_marco_a_leader())

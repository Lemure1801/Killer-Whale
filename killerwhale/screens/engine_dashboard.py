"""
KillerWhale — Complete Dashboard Engine Screen
Unifies TopTabBar (3.1), LeftOutputPanel (3.2), RightInteractivePanel (3.3),
and the TAB Leader Key engine into a cohesive, keyboard-driven workstation interface.
"""

from typing import Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static
from textual.containers import Vertical, Horizontal
from textual.events import Key

from killerwhale.core.leader import LeaderKeyManager
from killerwhale.core.output_stream import OutputFeedManager
from killerwhale.layout.top_bar import TopTabBar, TabSearchModal, TabListModal, TAB_DEFINITIONS
from killerwhale.layout.panels import LeftOutputPanel, RightInteractivePanel
from killerwhale.widgets.ascii_image import AsciiImageWidget
from killerwhale.theme import HEX_FG, HEX_FG_BRIGHT, HEX_FG_DIM, HEX_WHITE, HEX_SURFACE, HEX_BG


class DashboardEngineScreen(Screen):
    """
    Main Engine Dashboard Screen featuring dual-panel layout and leader navigation.
    """

    DEFAULT_CSS = f"""
    DashboardEngineScreen {{
        background: #000000;
        color: {HEX_FG};
    }}
    #engine-main-container {{
        height: 100%;
    }}
    #panels-split-row {{
        height: 1fr;
        margin: 0 1;
    }}
    .footer-status-bar {{
        dock: bottom;
        height: 1;
        background: {HEX_SURFACE};
        border-top: solid {HEX_FG_DIM};
        padding: 0 1;
        color: {HEX_FG_BRIGHT};
    }}
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.leader = LeaderKeyManager(timeout=1.5, on_state_change=self._on_leader_state_change)
        self._setup_leader_bindings()

    def _setup_leader_bindings(self) -> None:
        # TAB + 0..9
        self.leader.register_digit_action(self.action_jump_tab)

        # TAB + Ctrl + / (typing mode toggle)
        self.leader.register_action("ctrl+slash", self.action_toggle_typing)

        # TAB + Shift + / (tab fuzzy search modal)
        self.leader.register_action("shift+slash", self.action_open_tab_search)

        # TAB + Shift + L (full tab list modal)
        self.leader.register_action("shift+l", self.action_open_tab_list)

        # TAB + Ctrl + Left / Right (sub-tab switching)
        self.leader.register_action("ctrl+left", lambda: self.action_switch_subtab(-1))
        self.leader.register_action("ctrl+right", lambda: self.action_switch_subtab(1))

        # TAB + Ctrl + W (close interactive terminal)
        self.leader.register_action("ctrl+w", self.action_close_terminal)

        # TAB + Ctrl + T (open new interactive terminal)
        self.leader.register_action("ctrl+t", self.action_new_terminal)

    def compose(self) -> ComposeResult:
        with Vertical(id="engine-main-container"):
            self.top_bar = TopTabBar(id="engine-top-bar")
            yield self.top_bar

            with Horizontal(id="panels-split-row"):
                self.left_panel = LeftOutputPanel(id="engine-left-panel")
                yield self.left_panel

                self.right_panel = RightInteractivePanel(id="engine-right-panel")
                yield self.right_panel

            with Horizontal(classes="footer-status-bar"):
                self.lbl_footer = Label(
                    "KILLERWHALE OS v4 // [TAB] Prefixo Leader | [TAB+Ctrl+/] Digitação | [TAB+Shift+/] Busca Abas",
                    id="footer-hint"
                )
                yield self.lbl_footer

    def on_mount(self) -> None:
        self.set_interval(0.1, self.leader.check_timeout)
        self.feed_manager = OutputFeedManager(self.left_panel.write_output)
        # Seed feeds with real data
        self.feed_manager.update_local_network_feed()
        self.feed_manager.update_telemetry_feed()
        self.feed_manager.probe_target_feed()
        # Non-blocking periodic telemetry stream (every 2.0s to respect performance)
        self.set_interval(2.0, self.feed_manager.update_telemetry_feed)

    def on_unmount(self) -> None:
        """Ensures all interactive terminal PTY processes are terminated cleanly."""
        if hasattr(self, "right_panel"):
            self.right_panel.close_all()


    def _on_leader_state_change(self, is_active: bool) -> None:
        self.top_bar.leader_active = is_active
        if is_active:
            self.lbl_footer.update(">> MODO LÍDER ATIVO (Pressione 0-9, Ctrl+/, Shift+/, Shift+L, Ctrl+Left/Right) <<")
        else:
            self.lbl_footer.update("KILLERWHALE OS v4 // [TAB] Prefixo Leader | [TAB+Ctrl+/] Digitação | [TAB+Shift+/] Busca Abas")

    def on_key(self, event: Key) -> None:
        # 1. Leader key interception
        handled = self.leader.handle_key(event)
        if handled:
            return

        # 2. If typing mode is active and right panel is focused/active, forward key to right terminal
        if self.right_panel.typing_enabled and hasattr(self.right_panel, "handle_terminal_key"):
            self.right_panel.handle_terminal_key(event)

    def action_jump_tab(self, tab_index: int) -> None:
        """TAB + 0..9: Selects top tab."""
        if 0 <= tab_index < len(TAB_DEFINITIONS):
            self.top_bar.active_index = tab_index
            self.left_panel.write_output(
                0, f"[#00ffd1][✓] Alternado para aba {tab_index}: {TAB_DEFINITIONS[tab_index][1].upper()}[/]"
            )

    def action_toggle_typing(self) -> None:
        """TAB + Ctrl + /: Toggles typing mode in interactive panel."""
        active = self.right_panel.toggle_typing()
        msg = "[✓] Modo digitação ATIVADO no terminal interativo." if active else "[i] Modo digitação BLOQUEADO."
        self.left_panel.write_output(0, f"[#4dffef]{msg}[/]")

    def action_open_tab_search(self) -> None:
        """TAB + Shift + /: Opens tab search modal."""
        def on_selected(tab_idx: Optional[int]) -> None:
            if tab_idx is not None:
                self.action_jump_tab(tab_idx)
        self.app.push_screen(TabSearchModal(), on_selected)

    def action_open_tab_list(self) -> None:
        """TAB + Shift + L: Opens full tab list modal."""
        def on_selected(tab_idx: Optional[int]) -> None:
            if tab_idx is not None:
                self.action_jump_tab(tab_idx)
        self.app.push_screen(TabListModal(), on_selected)

    def action_switch_subtab(self, delta: int) -> None:
        """TAB + Ctrl + Left / Right: Alterna entre as sub-abas do terminal de output (read-only)."""
        self.left_panel.switch_subtab(delta)


    def action_close_terminal(self) -> None:
        """TAB + Ctrl + W: Closes current terminal in right panel."""
        closed = self.right_panel.close_current_terminal()
        if closed:
            self.left_panel.write_output(0, "[#ff3355][i] Terminal interativo encerrado com sucesso.[/]")

    def action_new_terminal(self) -> None:
        """TAB + Ctrl + T: Opens new terminal tab in right panel."""
        idx = self.right_panel.add_terminal()
        self.left_panel.write_output(0, f"[#00ffd1][✓] Nova sessão de terminal aberta: Terminal {idx+1}.[/]")

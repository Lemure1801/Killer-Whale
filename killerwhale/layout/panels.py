"""
KillerWhale — Left (Read-Only Output) and Right (Interactive Terminal) Panels
Implements layout sections 3.2 and 3.3 with internal sub-tabs and typing mode state.
"""

from typing import List, Dict, Optional
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label, Static, RichLog
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive

from killerwhale.theme import HEX_FG, HEX_FG_BRIGHT, HEX_FG_DIM, HEX_WHITE, HEX_SURFACE, HEX_BG, HEX_ALERT


class LeftOutputPanel(Widget):
    """
    Section 3.2: Left read-only output panel with context-specific sub-tabs.
    The user NEVER types directly here.
    Sub-tabs switched via TAB + Ctrl + Left / Right.
    """

    DEFAULT_CSS = f"""
    LeftOutputPanel {{
        width: 50%;
        height: 100%;
        border: solid {HEX_FG_DIM};
        background: {HEX_SURFACE};
        padding: 0 1;
    }}
    LeftOutputPanel:focus-within {{
        border: solid {HEX_FG};
    }}
    .panel-header {{
        height: 1;
        margin-top: 1;
        color: {HEX_FG_BRIGHT};
        text-style: bold;
    }}
    .subtabs-bar {{
        height: 1;
        margin: 1 0;
        align: left middle;
    }}
    .subtab-badge {{
        padding: 0 1;
        margin-right: 1;
        color: {HEX_FG_DIM};
        text-style: bold;
    }}
    .subtab-badge-active {{
        padding: 0 1;
        margin-right: 1;
        background: {HEX_FG};
        color: #000000;
        text-style: bold;
    }}
    .output-content {{
        height: 1fr;
        border: solid {HEX_FG_DIM};
        background: #000000;
    }}
    """

    active_subtab = reactive(0)

    SUBTABS: List[str] = [
        "Resultado de comandos",
        "Rede local",
        "Rede alvo",
        "Telemetria",
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("┌─ TERMINAL DE OUTPUT (READ-ONLY) ──────────────────────────┐", classes="panel-header")
            with Horizontal(classes="subtabs-bar"):
                self.subtab_labels: List[Label] = []
                for idx, title in enumerate(self.SUBTABS):
                    lbl = Label(f"<{title}>", classes="subtab-badge-active" if idx == 0 else "subtab-badge")
                    self.subtab_labels.append(lbl)
                    yield lbl

            self.log_views: List[RichLog] = []
            for idx in range(len(self.SUBTABS)):
                log = RichLog(classes="output-content", highlight=True, markup=True)
                self.log_views.append(log)
                yield log

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subtab_history: List[List[str]] = [[] for _ in self.SUBTABS]

    def on_mount(self) -> None:
        self._update_visibility()
        # Seed initial content
        self.write_output(0, "[#00ffd1][i] Monitor de comandos em espera. Saídas de ferramentas aparecerão aqui.[/]")
        self.write_output(1, "[#00ffd1][i] Interfaces locais monitoradas via psutil.[/]")
        self.write_output(2, "[#00ffd1][i] Alvo em escopo: NÃO DEFINIDO.[/]")
        self.write_output(3, "[#00ffd1][i] Telemetria de CPU/RAM/Disco ativa.[/]")

    def switch_subtab(self, delta: int) -> None:
        """Cycles sub-tab index by delta (-1 or +1)."""
        new_idx = (self.active_subtab + delta) % len(self.SUBTABS)
        self.active_subtab = new_idx

    def watch_active_subtab(self, new_idx: int) -> None:
        for idx, lbl in enumerate(self.subtab_labels):
            if idx == new_idx:
                lbl.remove_class("subtab-badge")
                lbl.add_class("subtab-badge-active")
            else:
                lbl.remove_class("subtab-badge-active")
                lbl.add_class("subtab-badge")
        self._update_visibility()

    def _update_visibility(self) -> None:
        for idx, log in enumerate(self.log_views):
            log.display = (idx == self.active_subtab)

    def write_output(self, subtab_index: int, message: str) -> None:
        """Appends output to a specific sub-tab log view."""
        if 0 <= subtab_index < len(self.log_views):
            self.subtab_history[subtab_index].append(message)
            self.log_views[subtab_index].write(message)



from killerwhale.core.terminal_session import TerminalSession


class RightInteractivePanel(Widget):
    """
    Section 3.3: Right interactive terminal panel.
    Supports multiple simultaneous terminal sessions organized as sub-tabs.
    Runs real PTY processes (bash/sh), with typing enabled via TAB + Ctrl + /.
    """

    DEFAULT_CSS = f"""
    RightInteractivePanel {{
        width: 50%;
        height: 100%;
        border: solid {HEX_FG_DIM};
        background: {HEX_SURFACE};
        padding: 0 1;
        margin-left: 1;
    }}
    RightInteractivePanel:focus-within {{
        border: solid {HEX_FG};
    }}
    .panel-header {{
        height: 1;
        margin-top: 1;
        color: {HEX_FG_BRIGHT};
        text-style: bold;
    }}
    .subtabs-bar {{
        height: 1;
        margin: 1 0;
        align: left middle;
    }}
    .subtab-badge {{
        padding: 0 1;
        margin-right: 1;
        color: {HEX_FG_DIM};
        text-style: bold;
    }}
    .subtab-badge-active {{
        padding: 0 1;
        margin-right: 1;
        background: {HEX_FG};
        color: #000000;
        text-style: bold;
    }}
    .typing-status {{
        height: 1;
        margin-bottom: 1;
        text-style: bold;
    }}
    .typing-disabled {{
        color: {HEX_FG_DIM};
    }}
    .typing-enabled {{
        color: {HEX_FG_BRIGHT};
        background: #002b24;
    }}
    .term-container {{
        height: 1fr;
        border: solid {HEX_FG_DIM};
        background: #000000;
    }}
    """

    typing_enabled = reactive(False)
    active_terminal_idx = reactive(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.terminal_titles: List[str] = []
        self.terminal_views: List[RichLog] = []
        self.sessions: List[TerminalSession] = []
        self._term_counter = 0

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("┌─ TERMINAIS INTERATIVOS (SESSÕES SIMULTÂNEAS) ───────────┐", classes="panel-header")
            
            self.bar_subtabs = Horizontal(classes="subtabs-bar")
            yield self.bar_subtabs

            self.lbl_typing = Label(
                "[DIGITAÇÃO: BLOQUEADA // Pressione TAB + Ctrl + / para ativar]",
                classes="typing-status typing-disabled"
            )
            yield self.lbl_typing

            self.term_box = Vertical(classes="term-container", id="term-box-container")
            yield self.term_box

    def on_mount(self) -> None:
        # Create initial terminal session 1
        self.add_terminal("Terminal 1")

    def toggle_typing(self) -> bool:
        """Toggles interactive typing mode."""
        self.typing_enabled = not self.typing_enabled
        return self.typing_enabled

    def watch_typing_enabled(self, enabled: bool) -> None:
        if enabled:
            self.lbl_typing.update(">> DIGITAÇÃO HABILITADA [Sessão Interativa Ativa] <<")
            self.lbl_typing.remove_class("typing-disabled")
            self.lbl_typing.add_class("typing-enabled")
        else:
            self.lbl_typing.update("[DIGITAÇÃO: BLOQUEADA // Pressione TAB + Ctrl + / para ativar]")
            self.lbl_typing.remove_class("typing-enabled")
            self.lbl_typing.add_class("typing-disabled")

    def _rebuild_subtabs_bar(self) -> None:
        self.bar_subtabs.remove_children()
        self.subtab_badges: List[Label] = []
        for idx, title in enumerate(self.terminal_titles):
            is_active = (idx == self.active_terminal_idx)
            lbl = Label(f"[{idx+1}: {title}]", classes="subtab-badge-active" if is_active else "subtab-badge")
            self.subtab_badges.append(lbl)
            self.bar_subtabs.mount(lbl)

    def switch_subtab(self, delta: int) -> None:
        if not self.terminal_titles:
            return
        new_idx = (self.active_terminal_idx + delta) % len(self.terminal_titles)
        self.active_terminal_idx = new_idx

    def watch_active_terminal_idx(self, new_idx: int) -> None:
        if hasattr(self, "subtab_badges"):
            for idx, lbl in enumerate(self.subtab_badges):
                if idx == new_idx:
                    lbl.remove_class("subtab-badge")
                    lbl.add_class("subtab-badge-active")
                else:
                    lbl.remove_class("subtab-badge-active")
                    lbl.add_class("subtab-badge")
        if hasattr(self, "terminal_views"):
            for idx, view in enumerate(self.terminal_views):
                view.display = (idx == new_idx)

    def _on_pty_output(self, log_widget: RichLog, data: str) -> None:
        """Thread-safe callback appending output from child shell PTY."""
        clean_text = data.replace("\r\n", "\n").replace("\r", "")
        try:
            self.app.call_from_thread(log_widget.write, clean_text)
        except Exception:
            pass

    def add_terminal(self, title: Optional[str] = None) -> int:
        """Opens a new interactive terminal sub-tab with a real PTY process."""
        self._term_counter += 1
        name = title or f"Terminal {len(self.terminal_titles) + 1}"
        self.terminal_titles.append(name)

        new_log = RichLog(highlight=True, markup=False)
        self.terminal_views.append(new_log)
        self.term_box.mount(new_log)

        # Create real PTY session
        session = TerminalSession(
            title=name,
            on_output=lambda text, w=new_log: self._on_pty_output(w, text)
        )
        self.sessions.append(session)

        self.active_terminal_idx = len(self.terminal_titles) - 1
        self._rebuild_subtabs_bar()
        self.watch_active_terminal_idx(self.active_terminal_idx)
        return self.active_terminal_idx

    def close_current_terminal(self) -> bool:
        """Closes current terminal sub-tab and kills child process (TAB + Ctrl + W)."""
        if len(self.terminal_titles) <= 1:
            return False  # Keep at least one terminal open

        idx = self.active_terminal_idx

        # Cleanly terminate process & close PTY
        if idx < len(self.sessions):
            session = self.sessions.pop(idx)
            session.close()

        if idx < len(self.terminal_views):
            old_view = self.terminal_views.pop(idx)
            old_view.remove()

        self.terminal_titles.pop(idx)

        if self.active_terminal_idx >= len(self.terminal_titles):
            self.active_terminal_idx = len(self.terminal_titles) - 1

        self._rebuild_subtabs_bar()
        self.watch_active_terminal_idx(self.active_terminal_idx)
        return True

    def handle_terminal_key(self, event: Key) -> None:
        """Sends key event to currently active PTY session if typing is enabled."""
        if not self.typing_enabled:
            return
        if 0 <= self.active_terminal_idx < len(self.sessions):
            self.sessions[self.active_terminal_idx].write_key(event)

    def close_all(self) -> None:
        """Kills all PTY child sessions on app shutdown."""
        for session in self.sessions:
            session.close()
        self.sessions.clear()



"""
KillerWhale — Top Tab Bar & Modal Tab Selectors
Fixed top bar with tab indicators, leader mode badge, and modal dialogs
for tab fuzzy search (TAB + Shift + /) and tab list browsing (TAB + Shift + L).
"""

from typing import List, Tuple, Optional
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Static, Label, Input, OptionList
from textual.widgets.option_list import Option
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.binding import Binding

from killerwhale.theme import HEX_FG, HEX_FG_BRIGHT, HEX_FG_DIM, HEX_WHITE, HEX_SURFACE, HEX_BG


TAB_DEFINITIONS: List[Tuple[int, str, str]] = [
    (0, "Dashboard", "Painel Principal // Telemetria e Monitoramento Central"),
    (1, "Recon", "Varredura & Enumeração de Rede (Nmap Engine)"),
    (2, "Exploit", "Validação e Auditoria Controlada (Sqlmap Engine)"),
    (3, "Auditoria", "Registro e Análise de Logs de Segurança"),
    (4, "Cheatsheets", "Guias de Referência de Comandos em Markdown"),
    (5, "Manutenção", "Higienização de Caches, TRIM e Systemd Vacuum"),
]


class TabSearchModal(ModalScreen[Optional[int]]):
    """Fuzzy search modal triggered by TAB + Shift + /."""

    DEFAULT_CSS = f"""
    TabSearchModal {{
        align: center middle;
        background: rgba(0, 0, 0, 0.85);
    }}
    .search-box {{
        width: 64;
        height: auto;
        border: double {HEX_FG};
        background: {HEX_SURFACE};
        padding: 1 2;
    }}
    .modal-title {{
        color: {HEX_FG_BRIGHT};
        text-style: bold;
        content-align: center middle;
        margin-bottom: 1;
    }}
    #tab-search-input {{
        margin-bottom: 1;
        border: tall {HEX_FG_DIM};
    }}
    #tab-search-list {{
        height: 8;
        border: solid {HEX_FG_DIM};
    }}
    """

    BINDINGS = [
        Binding("escape", "dismiss_none", "Cancelar", show=True),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(classes="search-box"):
            yield Label("┌─ BUSCA DE ABAS (FUZZY MATCH) ────────────────────────┐", classes="modal-title")
            self.input_search = Input(placeholder="Digite o nome da aba...", id="tab-search-input")
            yield self.input_search
            self.opt_list = OptionList(id="tab-search-list")
            yield self.opt_list

    def on_mount(self) -> None:
        self.populate("")
        self.input_search.focus()

    def populate(self, query: str) -> None:
        self.opt_list.clear_options()
        self.filtered: List[Tuple[int, str, str]] = []
        q = query.lower().strip()
        for idx, title, desc in TAB_DEFINITIONS:
            if not q or q in title.lower() or q in desc.lower() or q == str(idx):
                self.filtered.append((idx, title, desc))
                self.opt_list.add_option(Option(f"[{idx}] {title.upper()} — {desc}", id=str(idx)))
        if self.filtered:
            self.opt_list.highlighted = 0

    def on_input_changed(self, event: Input.Changed) -> None:
        self.populate(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        idx = self.opt_list.highlighted
        if idx is not None and 0 <= idx < len(self.filtered):
            self.dismiss(self.filtered[idx][0])
        else:
            self.dismiss(None)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if 0 <= event.option_index < len(self.filtered):
            self.dismiss(self.filtered[event.option_index][0])

    def action_dismiss_none(self) -> None:
        self.dismiss(None)


class TabListModal(ModalScreen[Optional[int]]):
    """Full navigable tab list triggered by TAB + Shift + L."""

    DEFAULT_CSS = f"""
    TabListModal {{
        align: center middle;
        background: rgba(0, 0, 0, 0.85);
    }}
    .list-box {{
        width: 70;
        height: auto;
        border: double {HEX_FG};
        background: {HEX_SURFACE};
        padding: 1 2;
    }}
    .modal-title {{
        color: {HEX_FG_BRIGHT};
        text-style: bold;
        content-align: center middle;
        margin-bottom: 1;
    }}
    #full-tab-list {{
        height: 10;
        border: solid {HEX_FG_DIM};
        margin-bottom: 1;
    }}
    """

    BINDINGS = [
        Binding("escape", "dismiss_none", "Fechar", show=True),
        Binding("enter", "select_current", "Selecionar", show=True),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(classes="list-box"):
            yield Label("┌─ SELEÇÃO COMPLETA DE ABAS / WORKSPACES ──────────────┐", classes="modal-title")
            self.opt_list = OptionList(id="full-tab-list")
            yield self.opt_list

    def on_mount(self) -> None:
        self.opt_list.clear_options()
        for idx, title, desc in TAB_DEFINITIONS:
            self.opt_list.add_option(Option(f"[{idx}] {title.upper():<12} │ {desc}", id=str(idx)))
        self.opt_list.highlighted = 0
        self.opt_list.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if 0 <= event.option_index < len(TAB_DEFINITIONS):
            self.dismiss(TAB_DEFINITIONS[event.option_index][0])

    def action_select_current(self) -> None:
        idx = self.opt_list.highlighted
        if idx is not None and 0 <= idx < len(TAB_DEFINITIONS):
            self.dismiss(TAB_DEFINITIONS[idx][0])

    def action_dismiss_none(self) -> None:
        self.dismiss(None)


class TopTabBar(Widget):
    """
    Fixed top tab bar displaying workspace tabs and leader key badge.
    """

    DEFAULT_CSS = f"""
    TopTabBar {{
        dock: top;
        height: 3;
        background: {HEX_BG};
        border-bottom: solid {HEX_FG_DIM};
        padding: 0 1;
    }}
    .tabs-row {{
        height: 1;
        margin-top: 1;
        align: left middle;
    }}
    .tab-badge {{
        padding: 0 1;
        margin-right: 1;
        color: {HEX_FG_DIM};
        text-style: bold;
    }}
    .tab-badge-active {{
        padding: 0 1;
        margin-right: 1;
        background: {HEX_FG};
        color: #000000;
        text-style: bold;
    }}
    .leader-badge {{
        dock: right;
        padding: 0 1;
        color: {HEX_FG_DIM};
        text-style: bold;
    }}
    .leader-badge-active {{
        dock: right;
        padding: 0 1;
        background: {HEX_FG_BRIGHT};
        color: #000000;
        text-style: bold blink;
    }}
    """

    active_index = reactive(0)
    leader_active = reactive(False)

    def compose(self) -> ComposeResult:
        with Horizontal(classes="tabs-row"):
            self.tab_labels: List[Label] = []
            for idx, title, _ in TAB_DEFINITIONS:
                lbl = Label(f"[{idx}] {title.upper()}", classes="tab-badge-active" if idx == 0 else "tab-badge")
                self.tab_labels.append(lbl)
                yield lbl

            self.lbl_leader = Label("[TAB: LEADER]", classes="leader-badge")
            yield self.lbl_leader

    def watch_active_index(self, new_index: int) -> None:
        for idx, lbl in enumerate(self.tab_labels):
            if idx == new_index:
                lbl.remove_class("tab-badge")
                lbl.add_class("tab-badge-active")
            else:
                lbl.remove_class("tab-badge-active")
                lbl.add_class("tab-badge")

    def watch_leader_active(self, active: bool) -> None:
        if active:
            self.lbl_leader.update("[LEADER: TAB ATIVO]")
            self.lbl_leader.remove_class("leader-badge")
            self.lbl_leader.add_class("leader-badge-active")
        else:
            self.lbl_leader.update("[TAB: LEADER]")
            self.lbl_leader.remove_class("leader-badge-active")
            self.lbl_leader.add_class("leader-badge")

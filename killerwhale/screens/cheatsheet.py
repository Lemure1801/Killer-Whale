"""
KillerWhale — Native Cheatsheet Browser Screen
Replaces workspaces/00-dashboard/cheatsheet.sh with a native Markdown viewer,
option selection list, live filtering, and direct Neovim RPC editing.
"""

import os
import glob
from typing import List, Tuple
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Label, Input, Button, Markdown, OptionList
from textual.widgets.option_list import Option
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.binding import Binding

from killerwhale.theme import HEX_FG, HEX_FG_BRIGHT, HEX_FG_DIM, HEX_ACCENT, HEX_WHITE, HEX_SURFACE

ASCII_BANNER = """  _  ___ _ _     __          ___           _      
 | |/ (_) | |    \\ \\        / / |         | |     
 | ' / _| | | ___ \\ \\  /\\  / /| |__   __ _| | ___ 
 |  < | | | |/ _ \\ \\ \\/  \\/ / | '_ \\ / _` | |/ _ \\
 | . \\| | | |  __/  \\  /\\  /  | | | | (_| | |  __/
 |_|\\_\\_|_|_|\\___|   \\/  \\/   |_| |_|\\__,_|_|\\___|"""


def discover_cheatsheets() -> List[Tuple[str, str]]:
    """Finds all .md files in cheatsheets directory."""
    kw_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cheats_dir = os.path.join(kw_root, "cheatsheets")
    if not os.path.isdir(cheats_dir):
        return []
    files = sorted(glob.glob(os.path.join(cheats_dir, "*.md")))
    return [(os.path.basename(f), f) for f in files]


class CheatsheetScreen(Screen):
    """Integrated Cheatsheet Markdown Viewer Screen."""

    CSS = f"""
    #cheatsheet-layout {{
        height: 100%;
    }}
    #search-filter {{
        margin: 0 1 1 1;
    }}
    #content-split {{
        height: 1fr;
        margin: 0 1 1 1;
    }}
    #files-list {{
        width: 30%;
        height: 100%;
        border: solid {HEX_FG_DIM};
    }}
    #markdown-scroll {{
        width: 70%;
        height: 100%;
        border: solid {HEX_FG_DIM};
        background: {HEX_SURFACE};
        padding: 1 2;
        margin-left: 1;
    }}
    .cheat-btn-bar {{
        height: 3;
        margin: 1 1 1 1;
    }}
    """

    BINDINGS = [
        Binding("escape", "nav_dashboard", "Dashboard", show=True),
        Binding("0", "nav_dashboard", "Dashboard", show=False),
        Binding("e", "action_open_in_nvim", "Abrir no Neovim", show=True),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cheatsheets = discover_cheatsheets()
        self.filtered_cheats = list(self.cheatsheets)
        self.current_file: str = self.cheatsheets[0][1] if self.cheatsheets else ""

    def compose(self) -> ComposeResult:
        with Vertical(id="cheatsheet-layout"):
            yield Static(ASCII_BANNER, classes="ascii-banner")

            with Horizontal(classes="status-bar"):
                yield Label("GUIA DE COMANDOS & CHEATSHEETS // RENDERIZADOR NATIVO", classes="title-label")

            self.filter_input = Input(placeholder="Filtrar cheatsheets (ex: nmap, sqlmap, recon)...", id="search-filter")
            yield self.filter_input

            with Horizontal(id="content-split"):
                self.opt_list = OptionList(id="files-list")
                yield self.opt_list

                with VerticalScroll(id="markdown-scroll"):
                    initial_content = self.load_markdown(self.current_file)
                    self.md_view = Markdown(initial_content, id="markdown-viewer")
                    yield self.md_view

            with Horizontal(classes="cheat-btn-bar"):
                yield Button("📝 Abrir no Neovim [e]", id="btn-open-nvim", variant="primary")
                yield Button("Voltar ao Dashboard [ESC]", id="btn-back")

    def load_markdown(self, path: str) -> str:
        if path and os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"# Erro ao ler cheatsheet\n{e}"
        return "# Nenhum cheatsheet encontrado"

    def on_mount(self) -> None:
        self.populate_options("")

    def populate_options(self, query: str) -> None:
        self.opt_list.clear_options()
        self.filtered_cheats = []
        q = query.lower().strip()
        for name, path in self.cheatsheets:
            if not q or q in name.lower():
                self.filtered_cheats.append((name, path))
                self.opt_list.add_option(Option(f"📖 {name}", id=name))
        if self.filtered_cheats:
            self.opt_list.highlighted = 0
            self.load_selected(0)

    def on_input_changed(self, event: Input.Changed) -> None:
        self.populate_options(event.value)

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        if 0 <= event.option_index < len(self.filtered_cheats):
            self.load_selected(event.option_index)

    def load_selected(self, index: int) -> None:
        name, path = self.filtered_cheats[index]
        self.current_file = path
        content = self.load_markdown(path)
        self.md_view.update(content)

    def action_nav_dashboard(self) -> None:
        self.app.switch_to_screen("dashboard")

    def action_open_in_nvim(self) -> None:
        if self.current_file:
            self.app.open_neovim_action(target_file=self.current_file)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-open-nvim":
            self.action_open_in_nvim()
        elif event.button.id == "btn-back":
            self.action_nav_dashboard()

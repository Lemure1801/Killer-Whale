"""
KillerWhale — Native Command Palette & Screen Launcher
Replaces launcher/menu.sh and launcher/preview.sh with an integrated,
searchable Textual screen that preserves state across transitions.
"""

from dataclasses import dataclass
from typing import List, Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Label, Input, OptionList, Button
from textual.widgets.option_list import Option
from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding

from killerwhale.core.system import get_target
from killerwhale.theme import HEX_FG, HEX_FG_BRIGHT, HEX_FG_DIM, HEX_ACCENT, HEX_WHITE, HEX_SURFACE

ASCII_BANNER = """  _  ___ _ _     __          ___           _      
 | |/ (_) | |    \\ \\        / / |         | |     
 | ' / _| | | ___ \\ \\  /\\  / /| |__   __ _| | ___ 
 |  < | | | |/ _ \\ \\ \\/  \\/ / | '_ \\ / _` | |/ _ \\
 | . \\| | | |  __/  \\  /\\  /  | | | | (_| | |  __/
 |_|\\_\\_|_|_|\\___|   \\/  \\/   |_| |_|\\__,_|_|\\___|"""


@dataclass
class LauncherItem:
    id: str
    title: str
    category: str
    target_screen: str
    preview_desc: str
    extra_args: Optional[dict] = None


CATALOG: List[LauncherItem] = [
    LauncherItem(
        id="dash",
        title="[WS:00] Dashboard (Painel Central & Telemetria)",
        category="Workspaces",
        target_screen="dashboard",
        preview_desc="""[bold #66ff99]=== WORKSPACE 00: DASHBOARD ===[/bold #66ff99]
Painel principal de telemetria e controle do sistema.
Exibe CPU, Memória, Disco, Interfaces de Rede e Alvo ativo via psutil.
Atualização não-bloqueante e contínua em tempo real.

[bold #f0fff0]Atalho direto:[/bold #f0fff0] [bold #ffb000]0[/bold #ffb000] ou [bold #ffb000]ESC[/bold #ffb000]"""
    ),
    LauncherItem(
        id="recon",
        title="[WS:01] Recon (Reconhecimento & Enumeração)",
        category="Workspaces",
        target_screen="scanner",
        extra_args={"tool_type": "recon"},
        preview_desc="""[bold #66ff99]=== WORKSPACE 01: RECONHECIMENTO ===[/bold #66ff99]
Espaço integrado para varredura e enumeração de portas e serviços de rede.
Orquestra o Nmap Scanner com perfis rápidos, de serviços ou agressivos.
Saída estruturada e capacidade de exportação direta para o Neovim via RPC.

[bold #f0fff0]Atalho direto:[/bold #f0fff0] [bold #ffb000]1[/bold #ffb000]"""
    ),
    LauncherItem(
        id="exploit",
        title="[WS:02] Exploit (Auditoria & Validação)",
        category="Workspaces",
        target_screen="scanner",
        extra_args={"tool_type": "exploit"},
        preview_desc="""[bold #66ff99]=== WORKSPACE 02: EXPLOIT & AUDITORIA ===[/bold #66ff99]
Validação controlada de parâmetros vulneráveis e enumeração de banco de dados.
Orquestra o Sqlmap Runner com extração tabular de DBMS e técnicas confirmadas.
Logs com timestamp registrados e integrados ao editor.

[bold #f0fff0]Atalho direto:[/bold #f0fff0] [bold #ffb000]2[/bold #ffb000]"""
    ),
    LauncherItem(
        id="nmap_tool",
        title="[TOOL] Nmap Scanner (Orquestrador & Relatório)",
        category="Ferramentas",
        target_screen="scanner",
        extra_args={"tool_type": "recon"},
        preview_desc="""[bold #66ff99]=== NMAP SCANNER INTEGRADO ===[/bold #66ff99]
Execução monitorada do scanner Nmap.
Captura portas, estados e serviços em tabela formatada.
Permite abrir relatório diretamente no buffer do Neovim via RPC."""
    ),
    LauncherItem(
        id="sqlmap_tool",
        title="[TOOL] Sqlmap Runner (Auditoria SQLi)",
        category="Ferramentas",
        target_screen="scanner",
        extra_args={"tool_type": "exploit"},
        preview_desc="""[bold #66ff99]=== SQLMAP RUNNER INTEGRADO ===[/bold #66ff99]
Auditoria controlada de parâmetros vulneráveis.
Processamento de técnicas confirmadas e DBMS detectado."""
    ),
    LauncherItem(
        id="cleanup",
        title="[SYS] Limpeza & Higienização do Sistema",
        category="Sistema",
        target_screen="cleanup",
        preview_desc="""[bold #66ff99]=== HIGIENIZAÇÃO & LIMPEZA DO SISTEMA ===[/bold #66ff99]
Gerenciamento de espaço e resíduos:
- Limpeza de cache de pacotes (pacman / paccache)
- Remoção de pacotes órfãos
- Vacuum do systemd journalctl
- TRIM de SSD/Storage
- Limpeza de logs de auditoria do KillerWhale

[bold #f0fff0]Atalho direto:[/bold #f0fff0] [bold #ffb000]c[/bold #ffb000]"""
    ),
    LauncherItem(
        id="cheatsheets",
        title="[SYS] Cheatsheet Browser (Guias de Pentest)",
        category="Sistema",
        target_screen="cheatsheet",
        preview_desc="""[bold #66ff99]=== GUIA DE COMANDOS (CHEATSHEETS) ===[/bold #66ff99]
Visualizador de cheatsheets em Markdown nativo dentro do app:
- Referência geral de pentest e comandos essenciais
- Nmap cheatsheet detalhado
- Sqlmap cheatsheet
- Reconhecimento e enumeração de redes

[bold #f0fff0]Atalho direto:[/bold #f0fff0] [bold #ffb000]h[/bold #ffb000]"""
    ),
    LauncherItem(
        id="editor",
        title="[SYS] Neovim RPC (Notas & Relatórios)",
        category="Sistema",
        target_screen="neovim_action",
        preview_desc="""[bold #66ff99]=== INTEGRAÇÃO NEOVIM VIA RPC ===[/bold #66ff99]
Comunicação de processo duplo via socket IPC (/tmp/killerwhale-nvim.sock).
Envia relatórios, abre notas de auditoria e comanda buffers sem criar janelas avulsas.

[bold #f0fff0]Atalho direto:[/bold #f0fff0] [bold #ffb000]e[/bold #ffb000]"""
    ),
]


class LauncherScreen(Screen):
    """Command Palette & Screen Navigation Screen."""

    CSS = f"""
    #launcher-layout {{
        height: 100%;
    }}
    #search-box {{
        margin: 0 1 1 1;
    }}
    #split-container {{
        height: 1fr;
        margin: 0 1 1 1;
    }}
    #catalog-list {{
        width: 50%;
        height: 100%;
        border: solid {HEX_FG_DIM};
    }}
    #catalog-list:focus {{
        border: double {HEX_FG};
    }}
    #preview-panel {{
        width: 50%;
        height: 100%;
        border: solid {HEX_FG_DIM};
        background: {HEX_SURFACE};
        padding: 1;
        margin-left: 1;
    }}
    """

    BINDINGS = [
        Binding("escape", "nav_dashboard", "Voltar (Dashboard)", show=True),
        Binding("0", "nav_dashboard", "Dashboard", show=False),
        Binding("enter", "action_select", "Abrir Seleção", show=True),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="launcher-layout"):
            yield Static(ASCII_BANNER, classes="ascii-banner")
            
            with Horizontal(classes="status-bar"):
                yield Label(f"COMMAND PALETTE // ALVO ATIVO: [{get_target()}]", classes="title-label")

            self.search_input = Input(placeholder="Digite para filtrar comandos ou workspaces...", id="search-box")
            yield self.search_input

            with Horizontal(id="split-container"):
                self.opt_list = OptionList(id="catalog-list")
                yield self.opt_list

                with Vertical(id="preview-panel"):
                    yield Label("┌─ DETALHES & DOCUMENTAÇÃO ────────────────────────┐", classes="title-label")
                    self.lbl_preview = Static(CATALOG[0].preview_desc, id="preview-text")
                    yield self.lbl_preview

    def on_mount(self) -> None:
        self.populate_list("")
        self.opt_list.focus()

    def populate_list(self, filter_text: str) -> None:
        self.opt_list.clear_options()
        self.filtered_items = []
        q = filter_text.lower().strip()
        for idx, item in enumerate(CATALOG):
            if not q or q in item.title.lower() or q in item.category.lower():
                self.filtered_items.append(item)
                self.opt_list.add_option(Option(prompt=item.title, id=item.id))
        if self.filtered_items:
            self.opt_list.highlighted = 0
            self.update_preview(self.filtered_items[0])

    def on_input_changed(self, event: Input.Changed) -> None:
        self.populate_list(event.value)

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        if 0 <= event.option_index < len(self.filtered_items):
            item = self.filtered_items[event.option_index]
            self.update_preview(item)

    def update_preview(self, item: LauncherItem) -> None:
        self.lbl_preview.update(item.preview_desc)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if 0 <= event.option_index < len(self.filtered_items):
            item = self.filtered_items[event.option_index]
            self.activate_item(item)

    def activate_item(self, item: LauncherItem) -> None:
        if item.target_screen == "dashboard":
            self.action_nav_dashboard()
        elif item.target_screen == "neovim_action":
            self.app.open_neovim_action()
        else:
            args = item.extra_args or {}
            self.app.switch_to_screen(item.target_screen, **args)

    def action_nav_dashboard(self) -> None:
        self.app.switch_to_screen("dashboard")

    def action_select(self) -> None:
        idx = self.opt_list.highlighted
        if idx is not None and 0 <= idx < len(self.filtered_items):
            self.activate_item(self.filtered_items[idx])

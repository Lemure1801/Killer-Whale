"""
KillerWhale — System Cleanup Screen
Replaces workspaces/00-dashboard/cleanup.sh with an interactive Textual screen.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Label, Button, RichLog, OptionList
from textual.widgets.option_list import Option
from textual.containers import Vertical, Horizontal
from textual.binding import Binding

from killerwhale.core.cleanup import CLEANUP_TASKS, run_cleanup_task
from killerwhale.theme import HEX_FG, HEX_FG_BRIGHT, HEX_FG_DIM, HEX_ACCENT, HEX_WHITE, HEX_SURFACE

ASCII_BANNER = """  _  ___ _ _     __          ___           _      
 | |/ (_) | |    \\ \\        / / |         | |     
 | ' / _| | | ___ \\ \\  /\\  / /| |__   __ _| | ___ 
 |  < | | | |/ _ \\ \\ \\/  \\/ / | '_ \\ / _` | |/ _ \\
 | . \\| | | |  __/  \\  /\\  /  | | | | (_| | |  __/
 |_|\\_\\_|_|_|\\___|   \\/  \\/   |_| |_|\\__,_|_|\\___|"""


class CleanupScreen(Screen):
    """System Maintenance & Sanitization Screen."""

    CSS = f"""
    #cleanup-layout {{
        height: 100%;
    }}
    #task-split {{
        height: 1fr;
        margin: 0 1 1 1;
    }}
    #task-list {{
        width: 45%;
        height: 100%;
        border: solid {HEX_FG_DIM};
    }}
    #log-container {{
        width: 55%;
        height: 100%;
        border: solid {HEX_FG_DIM};
        background: {HEX_SURFACE};
        padding: 1;
        margin-left: 1;
    }}
    #cleanup-log {{
        height: 1fr;
        border: solid {HEX_FG_DIM};
    }}
    .cleanup-btn-bar {{
        height: 3;
        margin: 1 1 1 1;
    }}
    """

    BINDINGS = [
        Binding("escape", "nav_dashboard", "Dashboard", show=True),
        Binding("0", "nav_dashboard", "Dashboard", show=False),
        Binding("enter", "action_run_selected", "Executar Selecionada", show=True),
        Binding("a", "action_run_all", "Executar Todas", show=True),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="cleanup-layout"):
            yield Static(ASCII_BANNER, classes="ascii-banner")

            with Horizontal(classes="status-bar"):
                yield Label("CENTRAL DE HIGIENIZAÇÃO & LIMPEZA DO SISTEMA", classes="title-label")

            with Horizontal(id="task-split"):
                self.opt_list = OptionList(id="task-list")
                yield self.opt_list

                with Vertical(id="log-container"):
                    yield Label("┌─ LOG DE EXECUÇÃO & STATUS ────────────────────────┐", classes="title-label")
                    self.log_view = RichLog(id="cleanup-log", highlight=True, markup=True)
                    yield self.log_view

            with Horizontal(classes="cleanup-btn-bar"):
                yield Button("▶ Executar Selecionada [ENTER]", id="btn-run-sel", variant="primary")
                yield Button("⚡ Executar TODAS as Limpezas [a]", id="btn-run-all")
                yield Button("Limpar Log", id="btn-clear-log")
                yield Button("Voltar ao Dashboard [ESC]", id="btn-back")

    def on_mount(self) -> None:
        self.opt_list.clear_options()
        for idx, task in enumerate(CLEANUP_TASKS):
            root_badge = " [sudo]" if task.requires_root else ""
            self.opt_list.add_option(Option(f"[{idx+1}] {task.title}{root_badge}", id=task.id))
        self.opt_list.highlighted = 0
        self.log_view.write("[#66ff99][i] Selecione uma tarefa de manutenção ou pressione [a] para todas.[/]")

    def action_nav_dashboard(self) -> None:
        self.app.switch_to_screen("dashboard")

    def action_run_selected(self) -> None:
        idx = self.opt_list.highlighted
        if idx is not None and 0 <= idx < len(CLEANUP_TASKS):
            task = CLEANUP_TASKS[idx]
            self.execute_task(task)

    def action_run_all(self) -> None:
        self.log_view.write("[bold #ffb000][*] Iniciando rotina completa de higienização...[/bold #ffb000]")
        for task in CLEANUP_TASKS:
            self.execute_task(task)
        self.log_view.write("[bold #00ff66][✓] Todas as tarefas de manutenção foram concluídas![/bold #00ff66]")

    def execute_task(self, task) -> None:
        self.log_view.write(f"[*] Executando: [bold]{task.title}[/bold] ({task.description})...")
        ok, msg = run_cleanup_task(task.id)
        color = "#00ff66" if ok else "#ff3333"
        self.log_view.write(f"[{color}]{msg}[/{color}]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        b_id = event.button.id
        if b_id == "btn-run-sel":
            self.action_run_selected()
        elif b_id == "btn-run-all":
            self.action_run_all()
        elif b_id == "btn-clear-log":
            self.log_view.clear()
        elif b_id == "btn-back":
            self.action_nav_dashboard()

"""
KillerWhale — Real-time Reactive Dashboard Screen
Substitutes workspaces/00-dashboard/dashboard.sh with a non-flickering,
asynchronously updating reactive dashboard using psutil.
"""

from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Static, Label, Button, Input, ProgressBar
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.reactive import reactive
from textual.binding import Binding

from killerwhale.core.system import (
    take_system_snapshot,
    set_target,
    get_target,
    SystemSnapshot
)
from killerwhale.theme import (
    HEX_FG,
    HEX_FG_BRIGHT,
    HEX_FG_DIM,
    HEX_ACCENT,
    HEX_ALERT,
    HEX_WHITE,
    HEX_SURFACE,
    HEX_BG
)

ASCII_BANNER = """  _  ___ _ _     __          ___           _      
 | |/ (_) | |    \\ \\        / / |         | |     
 | ' / _| | | ___ \\ \\  /\\  / /| |__   __ _| | ___ 
 |  < | | | |/ _ \\ \\ \\/  \\/ / | '_ \\ / _` | |/ _ \\
 | . \\| | | |  __/  \\  /\\  /  | | | | (_| | |  __/
 |_|\\_\\_|_|_|\\___|   \\/  \\/   |_| |_|\\__,_|_|\\___|"""


class TargetModal(ModalScreen[str]):
    """Modal dialog to set or clear pentest scope target."""

    CSS = f"""
    TargetModal {{
        align: center middle;
        background: rgba(5, 10, 5, 0.85);
    }}
    .modal-box {{
        width: 60;
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
    .modal-buttons {{
        margin-top: 1;
        align: center middle;
        height: 3;
    }}
    """

    def compose(self) -> ComposeResult:
        current = get_target()
        with Vertical(classes="modal-box"):
            yield Label("┌────────────────────────────────────────────────────────┐", classes="metric-value")
            yield Label("│         DEFINIR ALVO / ESCOPO DE AUDITORIA             │", classes="modal-title")
            yield Label("└────────────────────────────────────────────────────────┘", classes="metric-value")
            yield Label("Digite o IP ou hostname do alvo (ou deixe vazio para limpar):", classes="metric-value")
            self.input_field = Input(value="" if current == "NÃO DEFINIDO" else current, placeholder="ex: 192.168.1.100 ou lab.local")
            yield self.input_field
            with Horizontal(classes="modal-buttons"):
                yield Button("Salvar", id="btn-save", variant="primary")
                yield Button("Limpar", id="btn-clear")
                yield Button("Cancelar", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            val = self.input_field.value.strip()
            self.dismiss(val)
        elif event.button.id == "btn-clear":
            self.dismiss("")
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip())


class DashboardScreen(Screen):
    """Real-time reactive telemetry and navigation dashboard."""

    BINDINGS = [
        Binding("1", "nav_recon", "Recon (WS:01)", show=True),
        Binding("2", "nav_exploit", "Exploit (WS:02)", show=True),
        Binding("m", "nav_launcher", "Launcher/Palette", show=True),
        Binding("c", "nav_cleanup", "Limpeza", show=True),
        Binding("h", "nav_cheatsheet", "Cheatsheet", show=True),
        Binding("e", "nav_editor", "Neovim", show=True),
        Binding("t", "action_set_target", "Alvo", show=True),
        Binding("r", "action_refresh", "Atualizar", show=True),
    ]

    # Reactive variables for live non-flickering telemetry
    cpu_val = reactive(0.0)
    mem_used = reactive(0)
    mem_total = reactive(0)
    mem_pct = reactive(0.0)
    disk_used = reactive(0.0)
    disk_total = reactive(0.0)
    disk_pct = reactive(0.0)
    net_info = reactive("Detectando...")
    uptime_info = reactive("Calculando...")
    host_info = reactive("Linux")
    active_target = reactive("NÃO DEFINIDO")
    tick_count = reactive(0)

    def compose(self) -> ComposeResult:
        with Vertical(id="dash-container"):
            # ASCII Art Banner
            yield Static(ASCII_BANNER, classes="ascii-banner")

            # System Header Info
            with Horizontal(classes="status-bar"):
                self.lbl_system = Label("PAINEL DE CONTROLE TUI // Carregando...", classes="title-label")
                yield self.lbl_system

            # Telemetry Metrics Grid
            with Vertical(classes="box-panel", id="telemetry-panel"):
                yield Label("┌─ TELEMETRIA DE RECURSOS EM TEMPO REAL ────────────────────────┐", classes="title-label")

                # Target Row
                with Horizontal(classes="metric-row"):
                    yield Label("ALVO ATIVO       :", classes="metric-label")
                    self.lbl_target = Label(self.active_target, classes="metric-amber")
                    yield self.lbl_target

                # CPU Row
                with Horizontal(classes="metric-row"):
                    yield Label("CPU (CARGA)      :", classes="metric-label")
                    self.lbl_cpu = Label("0.0%", classes="metric-value")
                    yield self.lbl_cpu
                self.bar_cpu = ProgressBar(total=100.0, show_eta=False, show_percentage=False)
                yield self.bar_cpu

                # Memory Row
                with Horizontal(classes="metric-row"):
                    yield Label("MEMÓRIA RAM      :", classes="metric-label")
                    self.lbl_mem = Label("0 MB / 0 MB (0%)", classes="metric-value")
                    yield self.lbl_mem
                self.bar_mem = ProgressBar(total=100.0, show_eta=False, show_percentage=False)
                yield self.bar_mem

                # Disk Row
                with Horizontal(classes="metric-row"):
                    yield Label("DISCO RAIZ (/)   :", classes="metric-label")
                    self.lbl_disk = Label("0 GB / 0 GB (0%)", classes="metric-value")
                    yield self.lbl_disk
                self.bar_disk = ProgressBar(total=100.0, show_eta=False, show_percentage=False)
                yield self.bar_disk

                # Network Row
                with Horizontal(classes="metric-row"):
                    yield Label("REDE ATIVA       :", classes="metric-label")
                    self.lbl_net = Label(self.net_info, classes="metric-value")
                    yield self.lbl_net

            # Actions & Navigation Grid
            with Vertical(classes="box-panel", id="actions-panel"):
                yield Label("┌─ NAVEGAÇÃO & AÇÕES RÁPIDAS ───────────────────────────────────┐", classes="title-label")
                with Grid(id="nav-buttons-grid"):
                    yield Button("[1] Recon Workspace", id="btn-recon")
                    yield Button("[2] Exploit Workspace", id="btn-exploit")
                    yield Button("[m] Command Palette", id="btn-launcher")
                    yield Button("[c] Limpeza & Manutenção", id="btn-cleanup")
                    yield Button("[h] Cheatsheets", id="btn-cheatsheet")
                    yield Button("[e] Neovim RPC", id="btn-editor")
                    yield Button("[t] Definir Alvo", id="btn-target")
                    yield Button("[q] Sair do App", id="btn-quit", variant="error")

    def on_mount(self) -> None:
        """Starts real-time telemetry sampling timer."""
        self.update_telemetry()
        self.timer = self.set_interval(1.0, self.update_telemetry)

    def update_telemetry(self) -> None:
        """Polls psutil without blocking and updates reactive state."""
        snap = take_system_snapshot()
        self.cpu_val = snap.cpu_percent
        self.mem_used = snap.memory_used_mb
        self.mem_total = snap.memory_total_mb
        self.mem_pct = snap.memory_percent
        self.disk_used = snap.disk_used_gb
        self.disk_total = snap.disk_total_gb
        self.disk_pct = snap.disk_percent

        net_parts = [f"{name}: {ip}" for name, ip in snap.net_interfaces]
        self.net_info = " | ".join(net_parts) if net_parts else "Sem conexões ativas"
        self.uptime_info = snap.uptime_str
        self.host_info = f"{snap.hostname} ({snap.kernel}) // {snap.uptime_str}"
        self.active_target = snap.active_target
        self.tick_count += 1

        # Push to UI widgets
        self.lbl_system.update(f"PAINEL DE CONTROLE TUI // {self.host_info}")
        self.lbl_target.update(f"[{self.active_target}]")
        self.lbl_cpu.update(f"{self.cpu_val:5.1f}%")
        self.bar_cpu.progress = self.cpu_val

        self.lbl_mem.update(f"{self.mem_used} MB / {self.mem_total} MB ({self.mem_pct:4.1f}%)")
        self.bar_mem.progress = self.mem_pct

        self.lbl_disk.update(f"{self.disk_used} GB / {self.disk_total} GB ({self.disk_pct:4.1f}%)")
        self.bar_disk.progress = self.disk_pct

        self.lbl_net.update(self.net_info)

    def action_refresh(self) -> None:
        """Manual refresh trigger."""
        self.update_telemetry()

    def action_set_target(self) -> None:
        """Opens modal dialog to set or clear target."""
        def handle_result(result: str | None) -> None:
            if result is not None:
                set_target(result)
                self.update_telemetry()

        self.app.push_screen(TargetModal(), handle_result)

    def action_nav_recon(self) -> None:
        self.app.switch_to_screen("scanner", tool_type="recon")

    def action_nav_exploit(self) -> None:
        self.app.switch_to_screen("scanner", tool_type="exploit")

    def action_nav_launcher(self) -> None:
        self.app.switch_to_screen("launcher")

    def action_nav_cleanup(self) -> None:
        self.app.switch_to_screen("cleanup")

    def action_nav_cheatsheet(self) -> None:
        self.app.switch_to_screen("cheatsheet")

    def action_nav_editor(self) -> None:
        self.app.open_neovim_action()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        b_id = event.button.id
        if b_id == "btn-recon":
            self.action_nav_recon()
        elif b_id == "btn-exploit":
            self.action_nav_exploit()
        elif b_id == "btn-launcher":
            self.action_nav_launcher()
        elif b_id == "btn-cleanup":
            self.action_nav_cleanup()
        elif b_id == "btn-cheatsheet":
            self.action_nav_cheatsheet()
        elif b_id == "btn-editor":
            self.action_nav_editor()
        elif b_id == "btn-target":
            self.action_set_target()
        elif b_id == "btn-quit":
            self.app.exit()

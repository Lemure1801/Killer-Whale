"""
KillerWhale — Interactive Scanner & Audit Screen
Executes Nmap & Sqlmap scans, parses findings in structured DataTables,
and allows opening reports directly in Neovim via RPC without leaving the interface.
"""

from typing import Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Label, Input, Button, DataTable, RichLog, Select
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.binding import Binding

from killerwhale.core.system import get_target, set_target
from killerwhale.core.orchestrator import execute_nmap_scan, execute_sqlmap_scan, ScanResult
from killerwhale.theme import HEX_FG, HEX_FG_BRIGHT, HEX_FG_DIM, HEX_ACCENT, HEX_WHITE, HEX_SURFACE

ASCII_BANNER = """  _  ___ _ _     __          ___           _      
 | |/ (_) | |    \\ \\        / / |         | |     
 | ' / _| | | ___ \\ \\  /\\  / /| |__   __ _| | ___ 
 |  < | | | |/ _ \\ \\ \\/  \\/ / | '_ \\ / _` | |/ _ \\
 | . \\| | | |  __/  \\  /\\  /  | | | | (_| | |  __/
 |_|\\_\\_|_|_|\\___|   \\/  \\/   |_| |_|\\__,_|_|\\___|"""


class ScannerScreen(Screen):
    """Integrated Recon & Exploit Audit Runner Screen."""

    CSS = f"""
    #scanner-container {{
        height: 100%;
    }}
    .config-panel {{
        height: auto;
        border: solid {HEX_FG_DIM};
        background: {HEX_SURFACE};
        padding: 1;
        margin: 0 1 1 1;
    }}
    .config-row {{
        height: 3;
        margin-bottom: 1;
        align: left middle;
    }}
    .config-label {{
        width: 14;
        color: {HEX_WHITE};
        text-style: bold;
    }}
    #target-input {{
        width: 40;
    }}
    #profile-select {{
        width: 32;
        margin-left: 1;
    }}
    .btn-row {{
        height: 3;
        margin-top: 1;
    }}
    #results-panel {{
        height: 1fr;
        border: solid {HEX_FG_DIM};
        background: {HEX_SURFACE};
        margin: 0 1 1 1;
        padding: 1;
    }}
    #findings-table {{
        height: 1fr;
        margin-bottom: 1;
    }}
    #status-lbl {{
        color: {HEX_ACCENT};
        text-style: bold;
    }}
    """

    BINDINGS = [
        Binding("escape", "nav_dashboard", "Dashboard", show=True),
        Binding("0", "nav_dashboard", "Dashboard", show=False),
        Binding("e", "action_open_in_nvim", "Abrir no Neovim", show=True),
        Binding("r", "action_run_scan", "Executar Varredura", show=True),
    ]

    def __init__(self, tool_type: str = "recon", **kwargs):
        super().__init__(**kwargs)
        self.tool_type = tool_type
        self.last_result: Optional[ScanResult] = None

    def compose(self) -> ComposeResult:
        with Vertical(id="scanner-container"):
            yield Static(ASCII_BANNER, classes="ascii-banner")

            title_str = "WORKSPACE 01: RECONHECIMENTO & ENUMERAÇÃO (NMAP)" if self.tool_type == "recon" else "WORKSPACE 02: EXPLOIT & VALIDAÇÃO (SQLMAP)"
            with Horizontal(classes="status-bar"):
                yield Label(f"{title_str} // ALVO ATIVO", classes="title-label")

            with Vertical(classes="config-panel"):
                with Horizontal(classes="config-row"):
                    yield Label("ALVO (IP/URL):", classes="config-label")
                    curr_target = get_target()
                    default_tgt = curr_target if curr_target != "NÃO DEFINIDO" else ("10.10.11.245" if self.tool_type == "recon" else "http://target.local/vuln?id=1")
                    self.input_target = Input(value=default_tgt, id="target-input")
                    yield self.input_target

                    yield Label("PERFIL:", classes="config-label")
                    if self.tool_type == "recon":
                        options = [
                            ("Serviços & Scripts (-sV -sC)", "services"),
                            ("Rápido (Top 100 portas)", "fast"),
                            ("Todas as Portas TCP (-p-)", "full"),
                            ("Detecção de SO & Agressivo (-A)", "aggressive"),
                        ]
                    else:
                        options = [
                            ("Detecção Batch (--batch)", "batch"),
                            ("Enumeração Banner (--batch --banner)", "banner"),
                        ]
                    self.select_profile = Select(options=options, value=options[0][1], id="profile-select")
                    yield self.select_profile

                with Horizontal(classes="btn-row"):
                    yield Button("▶ Executar Varredura [r]", id="btn-run", variant="primary")
                    yield Button("📝 Abrir Relatório no Neovim [e]", id="btn-open-nvim", disabled=True)
                    yield Button("Salvar Alvo no Escopo", id="btn-save-scope")
                    yield Button("Voltar ao Dashboard [ESC]", id="btn-back")

            with Vertical(id="results-panel"):
                self.lbl_status = Label("Pronto para executar varredura.", id="status-lbl")
                yield self.lbl_status

                self.table_findings = DataTable(id="findings-table")
                yield self.table_findings

    def on_mount(self) -> None:
        self.setup_table()

    def setup_table(self) -> None:
        self.table_findings.clear(columns=True)
        if self.tool_type == "recon":
            self.table_findings.add_columns("Porta / Proto", "Estado", "Serviço", "Versão / Banner")
        else:
            self.table_findings.add_columns("Categoria", "Resultado Encontrado")

    def action_nav_dashboard(self) -> None:
        self.app.switch_to_screen("dashboard")

    def action_run_scan(self) -> None:
        target = self.input_target.value.strip()
        if not target:
            self.lbl_status.update("[!] Erro: Alvo não especificado.")
            return

        self.lbl_status.update(f"[*] Executando auditoria em {target}...")
        profile = self.select_profile.value or "services"

        # Execute scan
        if self.tool_type == "recon":
            result = execute_nmap_scan(target=target, profile=profile)
            self.last_result = result
            self.display_nmap_results(result)
        else:
            result = execute_sqlmap_scan(target=target, mode=profile)
            self.last_result = result
            self.display_sqlmap_results(result)

        # Enable Neovim button
        btn_nvim = self.query_one("#btn-open-nvim", Button)
        btn_nvim.disabled = False
        self.lbl_status.update(
            f"[✓] Varredura finalizada em {result.duration_seconds}s (Código {result.return_code}). Log: {result.log_path}"
        )

    def display_nmap_results(self, result: ScanResult) -> None:
        self.table_findings.clear()
        if result.ports:
            for p in result.ports:
                state_styled = f"[bold #00ff66]{p.state}[/bold #00ff66]" if p.state == "open" else f"[#ffb000]{p.state}[/#ffb000]"
                self.table_findings.add_row(p.port, state_styled, p.service, p.version or "-")
        else:
            self.table_findings.add_row("N/A", "Fechado", "Nenhuma porta aberta detectada", "-")

    def display_sqlmap_results(self, result: ScanResult) -> None:
        self.table_findings.clear()
        summary = result.sql_summary
        dbms = summary.get("dbms", "N/A")
        params = ", ".join(summary.get("parameters", [])) or "Nenhum detectado"
        techs = ", ".join(summary.get("technique", [])) or "Nenhuma detectada"

        self.table_findings.add_row("DBMS Identificado", dbms)
        self.table_findings.add_row("Parâmetros Vulneráveis", params)
        self.table_findings.add_row("Técnicas Confirmadas", techs)

    def action_open_in_nvim(self) -> None:
        """Sends the generated audit report to the active Neovim instance via RPC."""
        if not self.last_result:
            self.notify("Execute uma varredura antes de abrir no editor.", title="Neovim RPC", severity="warning")
            return

        log_path = self.last_result.log_path
        self.app.open_neovim_action(target_file=log_path)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        b_id = event.button.id
        if b_id == "btn-run":
            self.action_run_scan()
        elif b_id == "btn-open-nvim":
            self.action_open_in_nvim()
        elif b_id == "btn-save-scope":
            target = self.input_target.value.strip()
            if target:
                set_target(target)
                self.notify(f"Alvo '{target}' salvo como escopo ativo.", title="Escopo", severity="information")
        elif b_id == "btn-back":
            self.action_nav_dashboard()

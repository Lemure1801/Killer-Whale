"""
KillerWhale — Central Application Engine v4
Full integration of Dashboard Engine, PTY Terminals, Leader Key system,
and Neovim RPC.
"""

import os
from typing import Optional
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.binding import Binding
from textual.events import Key

from killerwhale.theme import APP_CSS
from killerwhale.screens.engine_dashboard import DashboardEngineScreen
from killerwhale.screens.dashboard import DashboardScreen
from killerwhale.screens.launcher import LauncherScreen
from killerwhale.screens.scanner import ScannerScreen
from killerwhale.screens.cleanup import CleanupScreen
from killerwhale.screens.cheatsheet import CheatsheetScreen
from killerwhale.core.nvim_client import NeovimRPCClient, DEFAULT_NVIM_SOCK


class KillerWhaleApp(App):
    """KillerWhale Central Textual Application Engine."""

    CSS = APP_CSS
    TITLE = "KillerWhale OS"
    SUB_TITLE = "v4.0 // Phosphorescent Cyan Engine"

    BINDINGS = [
        Binding("q", "quit", "Sair", show=True, priority=True),
        Binding("ctrl+c", "quit", "Sair", show=False),
        Binding("0", "nav_dashboard", "Dashboard", show=True),
        Binding("m", "nav_launcher", "Launcher", show=True),
        Binding("e", "action_open_editor", "Neovim RPC", show=True),
    ]

    def __init__(self, legacy: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.legacy = legacy
        self.nvim_client = NeovimRPCClient()
        if not legacy:
            self.engine_dashboard = DashboardEngineScreen(name="dashboard")
        else:
            self.legacy_dashboard = DashboardScreen(name="dashboard")

    def on_mount(self) -> None:
        if not self.legacy:
            self.install_screen(self.engine_dashboard, name="dashboard")
        else:
            self.install_screen(self.legacy_dashboard, name="dashboard")

        self.install_screen(LauncherScreen(), name="launcher")
        self.push_screen("dashboard")

    def switch_to_screen(self, screen_name: str, **kwargs) -> None:
        """Central screen dispatcher across workspaces and tools."""
        if screen_name == "dashboard":
            self.action_nav_dashboard()
        elif screen_name == "launcher":
            self.action_nav_launcher()
        elif screen_name == "scanner":
            tool_type = kwargs.get("tool_type", "recon")
            self.push_screen(ScannerScreen(tool_type=tool_type))
        elif screen_name == "cleanup":
            self.push_screen(CleanupScreen())
        elif screen_name == "cheatsheet":
            self.push_screen(CheatsheetScreen())
        elif screen_name in self._installed_screens:
            self.push_screen(screen_name)
        else:
            self.notify(
                f"Tela '{screen_name}' selecionada.",
                title="Navegação",
                severity="information"
            )

    def action_nav_dashboard(self) -> None:
        """Switches to Dashboard screen while preserving underlying state."""
        if self.screen.name != "dashboard":
            self.pop_screen()

    def action_nav_launcher(self) -> None:
        """Opens Command Palette launcher from any screen."""
        if self.screen.name != "launcher":
            self.push_screen("launcher")

    def action_open_editor(self) -> None:
        self.open_neovim_action()

    def open_neovim_action(self, target_file: Optional[str] = None) -> None:
        """Dispatches an open action to the running Neovim instance via RPC."""
        target = target_file or os.path.expanduser("~/.killerwhale/target")
        if not os.path.exists(target):
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w") as f:
                f.write("# KillerWhale Scope Target & Notes\n")

        ok, msg = self.nvim_client.open_file(target)
        if ok:
            self.notify(f"Arquivo '{os.path.basename(target)}' aberto no Neovim via RPC.", title="Neovim RPC", severity="information")
        else:
            self.notify(f"Falha RPC: {msg}", title="Neovim RPC", severity="warning")

    async def action_quit(self) -> None:
        """Gracefully closes all child terminal PTY processes and exits."""
        if hasattr(self, "engine_dashboard") and hasattr(self.engine_dashboard, "right_panel"):
            self.engine_dashboard.right_panel.close_all()
        await super().action_quit()



def main():
    """CLI entrypoint."""
    app = KillerWhaleApp()
    app.run()


if __name__ == "__main__":
    main()

"""Py2048 TUI Application"""

from textual.app import App

from py2048.bootstrap import bootstrap
from py2048.interfaces.tui.screens import MainMenu
from py2048.service_layer.messagebus import MessageBus  # for type hinting


class Py2048TUIApp(App[None]):
    """Main TUI application class for the 2048 game."""

    TITLE = "Py2048"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("Q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(self, bus: MessageBus | None = None) -> None:
        super().__init__()
        self.bus = bootstrap() if not bus else bus

    def on_mount(self) -> None:
        """Initialize the application."""
        self.install_screen(MainMenu(bus=self.bus), name="main_menu")  # type: ignore
        # self.install_screen(GameScreen(bus=self.bus), name="game")  # type: ignore
        # self.install_screen(GameOverScreen(bus=self.bus), name="game_over")  # type: ignore
        self.push_screen("main_menu")

    async def action_quit(self) -> None:
        """Handle the quit action."""
        self.exit()


if __name__ == "__main__":  # pragma: no cover
    # Launch the Py2048 TUI app when run directly
    app = Py2048TUIApp()
    app.run()

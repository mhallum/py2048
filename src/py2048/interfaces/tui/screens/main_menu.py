"""Main menu screen for the Py2048 TUI application.

This module defines the `MainMenu` class, which renders the initial interface
for the terminal-based version of Py2048. It provides users with a keyboard-
navigable menu to start a new game, resume an existing one, or exit the application.

Classes:
    MainMenu: The main screen presented to the user at startup.
"""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Header,
    Label,
    OptionList,
)
from textual.widgets.option_list import Option

from py2048.core import commands
from py2048.interfaces.tui.screens.game_screen import GameScreen
from py2048.service_layer.messagebus import MessageBus  # for type hinting


class MainMenu(Screen[None]):
    """Main menu screen for the TUI application."""

    CSS_PATH = "../styles/main_menu.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("Q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(self, bus: MessageBus) -> None:
        """Initialize the main menu screen.
        Args:
            bus (MessageBus): The message bus used to communicate with the domain layer.
        """

        super().__init__()
        self.bus = bus
        self._resume_game_disabled = not self._has_resume_game()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Welcome to Py2048!", id="welcome-label")
        yield Label("Main Menu", id="main-menu-title")
        yield Container(
            OptionList(
                Option("New Game", id="new-game"),
                Option(
                    "Resume Game", id="resume-game", disabled=self._resume_game_disabled
                ),
                Option("Exit", id="exit"),
                id="main-menu-options",
            ),
            id="main-menu-container",
        )
        yield Footer()

    async def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        """Handle selection when Enter is pressed."""
        selected_id = event.option_id
        match selected_id:
            case "new-game":
                cmd = commands.StartNewGame(slot_id="current_game")
                self.bus.handle(cmd)
                self.enable_resume_game()
                await self.app.push_screen(GameScreen(bus=self.bus))  # type: ignore
            case "resume-game":
                await self.app.push_screen(GameScreen(bus=self.bus))  # type: ignore
            case "exit":
                self.app.exit()
            case _:  # pragma: no cover
                # fallback just in case no valid selection is made, but it should not happen.
                self.app.bell()

    def _has_resume_game(self) -> bool:
        """Determine whether there is a game in progress that can be resumed.

        Returns:
            bool: True if a current game exists and can be resumed, False otherwise.
        """

        if self.bus.uow.games.get("current_game") is None:  # TODO: add a view for this?
            return False
        return True

    def disable_resume_game(self) -> None:
        """Disable the 'Resume Game' option."""
        self._resume_game_disabled = True
        option_list = self.screen.query_one("#main-menu-options", OptionList)
        for option in option_list.options:
            if option.id == "resume-game":
                option.disabled = True
                break

    def enable_resume_game(self) -> None:
        """Enable the 'Resume Game' option."""
        self._resume_game_disabled = False
        option_list = self.screen.query_one("#main-menu-options", OptionList)
        for option in option_list.options:
            if option.id == "resume-game":
                option.disabled = False
                break

"""Main menu screen for the TUI application."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView

from py2048 import views
from py2048.core import commands
from py2048.service_layer.messagebus import MessageBus  # for type hinting


class MainMenu(Screen[None]):
    """Main menu screen for the TUI application."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("Q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(self, bus: MessageBus) -> None:
        super().__init__()
        self.bus = bus

    def compose(self) -> ComposeResult:
        """Create the main menu layout."""
        yield Header()
        yield ListView(
            ListItem(Label("New Game", id="new-game")),
            ListItem(Label("Resume Game", id="resume-game")),
            ListItem(Label("Exit", id="exit")),
            id="main-menu-list",
        )
        yield Footer()

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection when Enter is pressed."""
        selected_id = event.item.query_one(Label).id
        match selected_id:
            case "new-game":
                cmd = commands.StartNewGame(game_id="current_game")
                self.bus.handle(cmd)
                updated_values = views.game_screen_values(
                    uow=self.bus.uow, game_id="current_game"
                )
                self.app.get_screen("game").board.update_board(  # type: ignore
                    updated_values["grid"]
                )
                self.app.get_screen("game").scores.update_scores(  # type: ignore
                    score=updated_values["score"],
                    high_score=updated_values["high_score"],
                )
                self.app.switch_screen("game")  # type: ignore
            case "resume-game":
                self.app.switch_screen("game")  # type: ignore
            case "exit":
                self.app.exit()
            case _:
                self.app.bell()  # fallback

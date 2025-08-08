"""The game screen for the TUI interface of Py2048."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header

from py2048 import views
from py2048.core import commands
from py2048.interfaces.tui.screens.game_over_screen import GameOverScreen
from py2048.interfaces.tui.widgets import GameBoard, LabelValue
from py2048.service_layer.messagebus import MessageBus


class GameScreen(Screen[None]):
    """Screen for the game interface in the TUI."""

    CSS_PATH = "../styles/game_screen.tcss"

    BINDINGS = [
        ("up", "move('up')", "Move Up"),
        ("down", "move('down')", "Move Down"),
        ("left", "move('left')", "Move Left"),
        ("right", "move('right')", "Move Right"),
        ("q", "quit", "Quit"),
        ("Q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(self, bus: MessageBus) -> None:
        super().__init__()
        self.bus = bus

        slot_id = "current_game"

        if not (
            initial_values := views.query_game_screen_values_by_slot(
                slot_id, uow=self.bus.uow
            )
        ):
            # Handle the case where the game is not found
            self._score = 0
            self._high_score = 0
            self.board = GameBoard(
                grid=((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0))
            )  # Initialize with an empty board

        else:
            self._score = initial_values.score
            self._high_score = initial_values.high_score
            self.board = GameBoard(grid=initial_values.grid)

    def compose(self) -> ComposeResult:
        yield Header()
        yield LabelValue(label="Score", value=self._score, id="current-score")
        yield LabelValue(label="Best", value=self._high_score, id="high-score")
        yield Container(self.board, id="board-container")
        yield Footer()

    async def action_move(self, direction: str) -> None:
        """Handle the move action."""

        # TODO: handle this in a view to avoid coupling ui layer to domain layer
        game = self.bus.uow.games.get("current_game")
        assert game is not None
        game_uuid = game.game_uuid

        cmd = commands.MakeMove(game_uuid=game_uuid, direction=direction)
        self.bus.handle(cmd)
        updated_values = views.query_game_screen_values_by_slot(
            slot_id="current_game", uow=self.bus.uow
        )
        assert (
            updated_values is not None
        )  # TODO: remove this assertions. Handle the case where the game is not found
        self.board.update_board(updated_values.grid)
        self.update_score(updated_values.score)

        if updated_values.status == views.GameStatus.OVER:
            await self.app.push_screen(  # type: ignore
                GameOverScreen(final_score=updated_values.score)
            )

    async def action_quit(self) -> None:
        """Quit to the main menu."""
        await self.app.pop_screen()  # type: ignore

    def update_score(self, score: int) -> None:
        """Update the score display."""
        self._score = score
        score_label = self.query_one("#current-score", LabelValue)
        score_label.update_value(score)

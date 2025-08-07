"""The game screen for the TUI interface of Py2048."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header

from py2048 import views
from py2048.adapters.repositories import MissingGameError
from py2048.core import commands
from py2048.interfaces.tui.widgets import GameBoard, ScoreBoard
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

        initial_values: views.GameScreenDTO = self._get_initial_game_screen_values()
        self.board: GameBoard = GameBoard(grid=initial_values.grid)
        self.scores: ScoreBoard = ScoreBoard(
            score=initial_values.score,
            high_score=initial_values.high_score,
        )

    def _get_initial_game_screen_values(self) -> views.GameScreenDTO:
        """Retrieve initial game screen values."""
        try:
            return views.game_screen_values(uow=self.bus.uow, game_id="current_game")
        except MissingGameError:
            return views.GameScreenDTO(
                grid=(
                    (0, 0, 0, 0),
                    (0, 0, 0, 0),
                    (0, 0, 0, 0),
                    (0, 0, 0, 0),
                ),
                score=0,
                high_score=0,
                status=views.GameStatus.NEW,
            )

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()
        yield Container(self.scores, self.board, id="board-container")
        yield Footer()

    async def action_move(self, direction: str) -> None:
        """Handle the move action."""
        cmd = commands.MakeMove(game_id="current_game", direction=direction)
        self.bus.handle(cmd)
        updated_values = views.game_screen_values(
            uow=self.bus.uow, game_id="current_game"
        )
        self.board.update_board(updated_values.grid)
        self.scores.update_scores(
            score=updated_values.score, high_score=updated_values.high_score
        )

    async def action_quit(self) -> None:
        """Quit to the main menu."""
        self.app.switch_screen("main_menu")  # type: ignore

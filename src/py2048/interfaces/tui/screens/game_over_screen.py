"""Game Over Screen for the TUI Interface"""

from typing import ClassVar

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, Label

from py2048.interfaces.tui.widgets import LabelValue


class GameOverScreen(Screen[None]):
    """Screen for the game over interface in the TUI."""

    CSS_PATH = "../styles/game_over_screen.tcss"

    BINDINGS: ClassVar[list[Binding]] = []

    def __init__(self, final_score: int, high_score: int) -> None:
        super().__init__()
        self.final_score = final_score
        self.high_score = high_score

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()
        yield Label("GAME OVER!", id="game-over-title")
        yield LabelValue(label="Final Score", value=self.final_score, id="final-score")
        yield LabelValue(label="High Score", value=self.high_score, id="high-score")
        if self.final_score == self.high_score:
            # Display a special message if the final score is a new high score
            yield Label("✨ New High Score! ✨", id="new-high-score")
        yield Label(
            "Press any key to return to the main menu.", id="game-over-instructions"
        )
        yield Footer()

    async def on_key(self, event: events.Key) -> None:
        """Handle key events to return to the main menu."""
        event.stop()
        self.app.switch_screen("main_menu")  # type: ignore

"""CLI runner for the 2048 game.

This module provides the `CLIGameRunner` class, which manages the command-line interface for
playing 2048.
It handles rendering the game board, processing user input, and interacting with the game logic
via a message bus.

Classes:
    CLIGameRunner: Handles the main game loop, rendering, and user input for the CLI
    version of 2048.

Usage:
    Instantiate `CLIGameRunner` with a game ID, message bus, terminal, and console objects,
    then call `run()` to start the game.
"""

import time

from blessed import Terminal
from blessed.keyboard import Keystroke
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from py2048 import views
from py2048.core import commands
from py2048.service_layer.messagebus import MessageBus

TILE_WIDTH = 7  # Large enough to fit the largest possible tile value (131072)
USER_INPUT_INSTRUCTIONS = "Press ↑ ↓ ← → to merge tiles | Esc/Q to quit"
LOOP_TERMINATION_DELIMITER = "===END===\n"


class CLIGameRunner:
    """Runner for the CLI game interface."""

    def __init__(
        self,
        game_id: str,
        bus: MessageBus,
        term: Terminal,
        console: Console,
        test_mode: bool = False,
    ):
        self.term = term
        self.console = console
        self.bus = bus
        self.game_id = game_id
        self.running = False
        self.test_mode = test_mode

    def get_direction_from_key(self, key: Keystroke) -> str | None:
        """Map key presses to game move directions."""

        match key.code:
            case self.term.KEY_UP:
                return "up"
            case self.term.KEY_DOWN:
                return "down"
            case self.term.KEY_LEFT:
                return "left"
            case self.term.KEY_RIGHT:
                return "right"
            case _:
                return None

    def _make_table(self, grid: tuple[tuple[int, ...], ...]) -> Table:
        """Create a table for the game board."""

        table = Table(
            safe_box=True,
            show_header=False,
            show_lines=True,
            box=box.DOUBLE,
        )

        for _ in range(len(grid[0])):
            table.add_column("", width=TILE_WIDTH, justify="center", no_wrap=True)

        for row in grid:
            table.add_row(*[f"\n{value}\n" if value != 0 else "\n \n" for value in row])

        return table

    def render(self) -> None:
        """Render the game screen."""

        game_values = views.game_screen_values(game_id=self.game_id, uow=self.bus.uow)
        self.console.clear()
        self.console.print()  # adds an empy line for better spacing
        table = self._make_table(game_values["board"])
        scores = Text(
            f"Score: {game_values['score']}\nHigh Score: {game_values['high_score']}",
            justify="center",
        )
        self.console.print(scores, justify="center")
        self.console.print(table, justify="center")
        self.console.print(USER_INPUT_INSTRUCTIONS, justify="center", style="dim")

    def run(self) -> None:
        """Run the CLI game loop."""

        with (
            self.term.fullscreen(),
            self.term.cbreak(),
            self.term.hidden_cursor(),
        ):
            self.running = True
            while self.running:  # pylint: disable=while-used
                self.render()

                key = self.term.inkey()

                if key.code == self.term.KEY_ESCAPE or key in {"q", "Q"}:
                    self.console.print("Goodbye!", justify="center")
                    time.sleep(1)
                    self.running = False

                elif direction := self.get_direction_from_key(key):
                    cmd = commands.MakeMove(game_id=self.game_id, direction=direction)
                    self.bus.handle(cmd)

                if self.test_mode:
                    self.console.print(LOOP_TERMINATION_DELIMITER)

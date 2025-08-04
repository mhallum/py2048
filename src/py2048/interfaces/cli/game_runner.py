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
from rich.console import Console

from py2048 import views
from py2048.core import commands
from py2048.interfaces.cli.constants import LOOP_TERMINATION_DELIMITER
from py2048.interfaces.cli.game_screen import GameScreen
from py2048.service_layer.messagebus import MessageBus

TILE_WIDTH = 7  # Large enough to fit the largest possible tile value (131072)
USER_INPUT_INSTRUCTIONS = "Press ↑ ↓ ← → to merge tiles | Esc/Q to quit"


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

    def run(self) -> None:
        """Run the CLI game loop."""

        with (
            self.term.fullscreen(),
            self.term.cbreak(),
            self.term.hidden_cursor(),
        ):
            self.running = True
            while self.running:  # pylint: disable=while-used
                game_screen = GameScreen(
                    **views.game_screen_values(game_id=self.game_id, uow=self.bus.uow)
                )
                game_screen.render(self.console)

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

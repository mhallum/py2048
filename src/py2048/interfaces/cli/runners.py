"""CLI runner for the 2048 game.

Provides the `CLIGameRunner` class, which manages the command-line interface for
playing 2048. It handles game rendering, user input, and communication with the
core game logic through a message bus.

Classes:
    CLIGameRunner: Handles the game loop and input for the CLI version of 2048.

Usage:
    runner = CLIGameRunner(game_id, bus, term, console)
    runner.run()
"""

import time
from dataclasses import dataclass

from blessed import Terminal
from blessed.keyboard import Keystroke
from rich.console import Console

from py2048 import views
from py2048.core import commands
from py2048.interfaces.cli.constants import LOOP_TERMINATION_DELIMITER
from py2048.interfaces.cli.game_screen import GameScreen, InvalidGameScreenError
from py2048.service_layer.messagebus import MessageBus

TILE_WIDTH = 7  # Large enough to fit the largest possible tile value (131072)
USER_INPUT_INSTRUCTIONS = "Press ↑ ↓ ← → to merge tiles | Esc/Q to quit"


@dataclass
class DisplayIO:
    """Encapsulates the terminal and console for display purposes."""

    term: Terminal
    console: Console


class CLIGameRunner:
    """Runner for the CLI game interface."""

    def __init__(
        self,
        game_id: str,
        /,
        bus: MessageBus,
        display: DisplayIO,
        test_mode: bool = False,
    ):
        self.display = display
        self.bus = bus
        self.game_id = game_id
        self.running = False
        self.test_mode = test_mode

    def get_direction_from_key(self, key: Keystroke) -> str | None:
        """Convert a keystroke into a corresponding move direction for the game.

        Args:
            key (Keystroke): The keystroke object representing the user's input.

        Returns:
            str | None: The direction as a string ("up", "down", "left", "right") if the key
            matches a direction, otherwise None.
        """

        match key.code:
            case self.display.term.KEY_UP:
                return "up"
            case self.display.term.KEY_DOWN:
                return "down"
            case self.display.term.KEY_LEFT:
                return "left"
            case self.display.term.KEY_RIGHT:
                return "right"
            case _:
                return None

    def run(self) -> None:
        """Run the CLI game loop."""

        with (
            self.display.term.fullscreen(),
            self.display.term.cbreak(),
            self.display.term.hidden_cursor(),
        ):
            self.running = True
            while self.running:  # pylint: disable=while-used
                try:
                    game_screen = GameScreen(
                        **views.game_screen_values(
                            game_id=self.game_id, uow=self.bus.uow
                        )
                    )
                except InvalidGameScreenError:
                    self.display.console.print(
                        "[bold red]Error:[/] Unable to load game."
                    )
                    self.running = False
                    return

                game_screen.render(self.display.console)

                key = self.display.term.inkey()

                if key.code == self.display.term.KEY_ESCAPE or key in {"q", "Q"}:
                    self.display.console.print("Goodbye!", justify="center")
                    time.sleep(1)
                    self.running = False

                elif direction := self.get_direction_from_key(key):
                    cmd = commands.MakeMove(game_id=self.game_id, direction=direction)
                    self.bus.handle(cmd)

                if self.test_mode:
                    self.display.console.print(LOOP_TERMINATION_DELIMITER)

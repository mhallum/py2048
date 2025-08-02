"""CLI interface for Py2048."""

import time
from enum import Enum

from blessed import Terminal
from blessed.keyboard import Keystroke
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from py2048 import bootstrap
from py2048.application.menu import Menu
from py2048.core import commands
from py2048.interfaces.cli.constants import LOOP_TERMINATION_DELIMITER
from py2048.interfaces.cli.game_runner import CLIGameRunner
from py2048.service_layer.messagebus import MessageBus  # for type hinting

PADDING = 4


class MenuItem(str, Enum):
    """Enum for menu items."""

    NEW_GAME = "New Game"
    EXIT = "Exit"


class CLIMenuRunner:
    """Runner for the CLI menu."""

    def __init__(
        self, menu: Menu, term: Terminal, console: Console, test_mode: bool = False
    ):
        self.menu = menu
        self.term = term
        self.console = console
        self.running = False
        self.test_mode = test_mode

    def process_keypress(self, key: Keystroke):
        """Process a key press"""
        if key.code == self.term.KEY_UP:
            self.menu.move_up()
        elif key.code == self.term.KEY_DOWN:
            self.menu.move_down()
        elif key.code == self.term.KEY_ENTER:
            self.running = False

    def _render_menu_panel(self):
        table = Table.grid(padding=(0, 1))
        for i, item in enumerate(self.menu.items):
            label = item.value if isinstance(item, MenuItem) else item
            text = (
                Text(f"➤ {label}", style="reverse")
                if i == self.menu.index
                else Text(f"  {label}")
            )
            table.add_row(text)
        panel = Panel(table, title="Main Menu", padding=(1, 2))
        self.console.print(panel, justify="center")

    def render(self) -> None:
        """Render the menu in the terminal."""

        self.console.clear()
        self.console.print()
        self.console.print("Welcome to Py2048!", justify="center", style="bold")
        self.console.print()  # adds an empty line for better spacing
        self._render_menu_panel()
        self.console.print()
        self.console.print(
            "↑ ↓ to navigate | Enter to select", justify="center", style="dim"
        )
        self.console.print()

    def run(self) -> None:
        """Run the menu loop."""
        self.running = True
        while self.running:  # pylint: disable=while-used
            self.render()

            key = self.term.inkey()

            if key.code == self.term.KEY_UP:
                self.menu.move_up()
            elif key.code == self.term.KEY_DOWN:
                self.menu.move_down()
            elif key.code == self.term.KEY_ENTER:
                self.running = False

        if self.test_mode:
            self.console.print(LOOP_TERMINATION_DELIMITER)


def run_cli(
    bus: MessageBus,
    term: Terminal = Terminal(),
    console: Console = Console(),
    test_mode: bool = False,
) -> None:
    """Run the CLI version of the game."""

    menu = Menu("Welcome to Py2048!", [MenuItem.NEW_GAME, MenuItem.EXIT])
    menu_runner = CLIMenuRunner(menu, term, console)

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        menu_runner.running = True
        menu_runner.run()

        if menu.selected == MenuItem.NEW_GAME:
            print(term.center("Starting a new game..."))
            time.sleep(1)
            game_id = "new_game"

            cmd = commands.StartNewGame(game_id=game_id)
            bus.handle(cmd)

            game_runner = CLIGameRunner(
                game_id, bus, term, console, test_mode=test_mode
            )
            game_runner.run()

    if menu.selected == MenuItem.EXIT:
        print(term.center("Goodbye!"))
        time.sleep(1)


if __name__ == "__main__":  # pragma: no cover
    run_cli(bus=bootstrap.bootstrap(), term=Terminal(), console=Console())

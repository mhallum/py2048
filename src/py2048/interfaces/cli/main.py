"""CLI interface for Py2048."""

import time
from enum import Enum

from blessed import Terminal
from blessed.keyboard import Keystroke

from py2048.application.menu import Menu

PADDING = 4


class MenuItem(str, Enum):
    """Enum for menu items."""

    NEW_GAME = "New Game"
    EXIT = "Exit"


class CLIMenuRunner:
    """Runner for the CLI menu."""

    def __init__(self, menu: Menu, term: Terminal):
        self.menu = menu
        self.term = term
        self.running = False

    def process_keypress(self, key: Keystroke):
        """Process a key press"""
        if key.code == self.term.KEY_UP:
            self.menu.move_up()
        elif key.code == self.term.KEY_DOWN:
            self.menu.move_down()
        elif key.code == self.term.KEY_ENTER:
            self.running = False
        elif key.name in {"KEY_ESCAPE"} or key in {"q", "Q"}:
            self.running = False

    def _render_title(self, width: int) -> None:
        print(self.term.center("╔" + "═" * width + "╗"))
        print(self.term.center(f"║ {self.menu.title.center(width - 2)} ║"))
        print(self.term.center("╠" + "═" * width + "╣"))

    def _render_selected_item(self, item: str | MenuItem, width: int) -> None:
        label = item.value if isinstance(item, MenuItem) else item
        text = f"> {label}".ljust(width)
        print(self.term.center(f"║{self.term.reverse(text)}║"))

    def _render_unselected_item(self, item: str, width: int) -> None:
        print(self.term.center(f"║  {item.ljust(width - 2)}║"))

    def _render_items(self, width: int) -> None:
        for i, item in enumerate(self.menu.items):
            if i == self.menu.index:
                self._render_selected_item(item, width)
            else:
                self._render_unselected_item(item, width)

        print(self.term.center("╚" + "═" * width + "╝"))

    def _render_footer(self) -> None:
        msg = "↑ ↓ to navigate | Enter to select | Esc/Q to quit"
        print("\n" + self.term.center(self.term.dim + msg + self.term.normal))

    def _menu_width(self) -> int:
        content_width = max(len(item) for item in self.menu.items)
        title_width = len(self.menu.title)
        return max(content_width + PADDING, title_width + PADDING)  # padding

    def render(self) -> None:
        """Render the menu in the terminal."""
        width = self._menu_width()
        print(self.term.clear + self.term.move(0, 0))
        self._render_title(width)
        self._render_items(width)
        self._render_footer()


def run_cli(term: Terminal | None = None):
    """Run the CLI version of the game."""

    # Normally, we would just use `term = Terminal()`, but for testing, we allow passing a
    # mock terminal.
    # This allows us to simulate user input without requiring a real terminal.
    # If `term` is None (as is the case when not testing), we create a new Terminal instance.
    # This is useful for unit tests where we want to control the terminal behavior.
    if term is None:
        term = Terminal()  # pragma: no cover

    menu = Menu("Welcome to Py2048!", [MenuItem.NEW_GAME, MenuItem.EXIT])
    menu_runner = CLIMenuRunner(menu, term)
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        menu_runner.running = True
        while menu_runner.running:  # pylint: disable=while-used
            menu_runner.render()
            key = term.inkey()
            menu_runner.process_keypress(key)

        if menu.selected == MenuItem.EXIT:
            print(term.center("Goodbye!"))
            time.sleep(1)


if __name__ == "__main__":
    run_cli()  # pragma: no cover

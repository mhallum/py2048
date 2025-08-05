"""Menu logic for Py2048.

Defines a UI-independent representation of a menu, including selectable
items and navigation behavior. This module is part of the application layer and
can be reused across terminal, graphical, and web interfaces.
"""


class Menu:
    """A simple menu class for user interfaces."""

    def __init__(self, title: str, items: list[str]):
        self.title = title
        self.items = items
        self.index = 0

    def move_up(self):
        """Move the selection up in the menu."""
        self.index = (self.index - 1) % len(self.items)

    def move_down(self):
        """Move the selection down in the menu."""
        self.index = (self.index + 1) % len(self.items)

    @property
    def selected(self) -> str:
        """The current menu item."""
        return self.items[self.index]

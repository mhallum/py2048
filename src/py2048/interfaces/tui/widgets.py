"""Widgets for the TUI interface of the 2048 game."""

from rich import box
from rich.align import Align
from rich.table import Table
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label, Static


class GameBoard(Static):
    """A widget to display the game board in the TUI."""

    def __init__(self, grid: tuple[tuple[int, ...], ...]) -> None:
        super().__init__()
        self.grid = grid

    def on_mount(self) -> None:
        """Initialize the board view."""
        self.render_board()

    def render_board(self) -> None:
        """Render the game board as a table."""
        table = Table(show_header=False, box=box.DOUBLE, show_lines=True)

        for _ in range(4):
            table.add_column(justify="center", width=6)

        for row in self.grid:
            display_row = [f"\n{val:^6}\n" if val else "\n      \n" for val in row]
            table.add_row(*display_row)

        self.update(Align.center(table))

    def update_board(self, new_grid: tuple[tuple[int, ...], ...]) -> None:
        """Update the board with a new grid."""
        self.grid = new_grid
        self.render_board()


class LabelValue(Horizontal):
    """A simple label-value pair widget."""

    def __init__(
        self,
        label: str,
        value: str | int | float,
        **kwargs,  # type: ignore
    ) -> None:
        super().__init__(**kwargs)  # type: ignore
        self._label_text = label
        self._value_text = str(value)

    def compose(self) -> ComposeResult:
        yield Label(f"{self._label_text}:", id="label-part")
        yield Label(" ", id="spacer")
        yield Label(self._value_text, id="value-part")

    def update_value(self, new_value: str | int | float) -> None:
        """Update the value displayed."""
        value_label = self.query_one("#value-part", Label)
        value_label.update(str(new_value))

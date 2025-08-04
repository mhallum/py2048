import re
from dataclasses import dataclass
from functools import cached_property

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

TILE_WIDTH = 7  # Large enough to fit the largest possible tile value (131072)
USER_INPUT_INSTRUCTIONS = "Press ↑ ↓ ← → to merge tiles | Esc/Q to quit"


@dataclass(frozen=True)
class GameScreenParser:
    """Parser for a cli game screen output."""

    output: str

    @cached_property
    def score(self) -> int | None:
        """Extracts the displayed score from the console output.

        Assumes the score is displayed as "Score: <score>"
        (and that the High Score is displayed as "High Score: <high_score>")
        """

        if matches := re.findall(r"(?<!High )Score:\s*(\d+)", self.output):
            return int(matches[0])
        return None

    @cached_property
    def high_score(self) -> int | None:
        """Extracts the displayed high score from the console output.

        Assumes the high score is displayed as "High Score: <high_score>"
        """
        if match := re.search(r"High Score:\s*(\d+)", self.output):
            return int(match.group(1))
        return None

    @cached_property
    def lines(self) -> list[str]:
        """Splits the console output into lines."""
        return self.output.splitlines()

    @cached_property
    def grid_start_line_index(self) -> int:
        """Find the starting line index of the grid in the output."""
        for i, line in enumerate(self.lines):
            if "╔" in line:
                return i
        return 0

    @cached_property
    def grid_end_line_index(self) -> int:
        """Find the ending line index of the grid in the output."""
        for i, line in enumerate(self.lines):
            if "╚" in line:
                return i
        return len(self.lines) - 1

    @cached_property
    def grid(self) -> tuple[tuple[int, ...], ...]:
        """Extracts the game board grid from the console output.

        Assumes the grid is displayed in a table format with double lines
        and that each cell has a vertical padding of one space.
        """

        # Extract the rows from the console output
        rows = [
            self.lines[i].split("║")[1:-1]
            for i in range(self.grid_start_line_index + 2, self.grid_end_line_index, 4)
        ]

        # Convert the rows to integers, replacing empty cells with 0
        return tuple(
            tuple(int(cell.strip()) if cell.strip().isdigit() else 0 for cell in row)
            for row in rows
        )


@dataclass
class GameScreen:
    """Represents the game screen for the CLI interface."""

    grid: tuple[tuple[int, ...], ...]
    score: int
    high_score: int

    def _make_table(self) -> Table:
        """Create a table for the game board."""

        table = Table(
            safe_box=True,
            show_header=False,
            show_lines=True,
            box=box.DOUBLE,
        )

        for _ in range(len(self.grid[0])):
            table.add_column("", width=TILE_WIDTH, justify="center", no_wrap=True)

        for row in self.grid:
            table.add_row(*[f"\n{value}\n" if value != 0 else "\n \n" for value in row])

        return table

    def render(self, console: Console) -> None:
        """Render the game screen."""
        console.clear()
        console.print()  # adds an empty line for better spacing
        scores = Text(
            f"Score: {self.score}\nHigh Score: {self.high_score}",
            justify="center",
        )
        console.print(scores, justify="center")
        console.print(self._make_table(), justify="center")
        console.print(USER_INPUT_INSTRUCTIONS, justify="center", style="dim")

    @classmethod
    def from_output(cls, output: str) -> "GameScreen":
        """Recreate a GameScreen instance from a string output."""

        parser = GameScreenParser(output)
        if not parser.grid or parser.score is None or parser.high_score is None:
            raise ValueError("Invalid game screen output format")
        return cls(grid=parser.grid, score=parser.score, high_score=parser.high_score)

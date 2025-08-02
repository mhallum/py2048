"""Parser for the console output of the game runner."""

import re
from dataclasses import dataclass
from functools import cached_property

# pylint: disable=too-few-public-methods


def split_console_output_loops(
    output: str, loop_termination_delimiter: str
) -> list[str]:
    """Splits the console output by loop"""
    return output.split(loop_termination_delimiter)


@dataclass(frozen=True)
class ConsoleGameScreenParser:
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

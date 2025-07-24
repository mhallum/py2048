"""Module containing domain models for the 2048 game."""

# pylint: disable=too-few-public-methods

import random
from dataclasses import dataclass
from typing import overload

GRID_SIZE = 4


@overload
def _merge_tiles(tiles: list[int]) -> list[int]: ...
@overload
def _merge_tiles(tiles: tuple[int, ...]) -> tuple[int, ...]: ...
def _merge_tiles(tiles: list[int] | tuple[int, ...]) -> list[int] | tuple[int, ...]:
    """Merge a single row of tiles to the left."""
    new_row = [tile for tile in tiles if tile != 0]
    merged_row: list[int] = []
    skip = False
    for i, _ in enumerate(new_row):
        if skip:
            skip = False
            continue
        if i < len(new_row) - 1 and new_row[i] == new_row[i + 1]:
            merged_row.append(new_row[i] * 2)
            skip = True
        else:
            merged_row.append(new_row[i])
    merged_row.extend([0] * (GRID_SIZE - len(merged_row)))
    if isinstance(tiles, tuple):
        return tuple(merged_row)
    else:
        return list(merged_row)


def spawn_tile(board: "GameBoard") -> "GameBoard":
    """Spawn a new tile on the game board."""
    if positions := board.empty_tile_positions:
        i, j = random.choice(positions)
        new_grid = [list(row) for row in board.grid]
        new_grid[i][j] = 2
        return GameBoard(new_grid)
    return board


@dataclass
class GameBoard:
    """Class representing the game board for 2048."""

    grid: tuple[tuple[int, ...], ...]

    def __init__(self, grid: list[list[int]] | None = None):
        if grid is not None:
            self.grid = tuple(tuple(row) for row in grid)
        else:
            self.grid = tuple(
                tuple(0 for _ in range(GRID_SIZE)) for _ in range(GRID_SIZE)
            )
            self._add_random_tile()
            self._add_random_tile()

    def _add_random_tile(self):
        if positions := self.empty_tile_positions:
            i, j = random.choice(positions)
            new_grid = [list(row) for row in self.grid]
            new_grid[i][j] = 2
            self.grid = tuple(tuple(row) for row in new_grid)

    @property
    def height(self) -> int:
        """Get the height (number of rows) of the game board."""
        return len(self.grid)

    @property
    def width(self) -> int:
        """Get the width (number of columns) of the game board."""
        return len(self.grid[0])

    @property
    def empty_tile_positions(self) -> list[tuple[int, int]]:
        """Get the positions (row, col) of empty tiles on the board."""
        return [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
            if self.grid[i][j] == 0
        ]

    def shift_left(self):
        """Shift tiles to the left."""
        self.grid = tuple(_merge_tiles(row) for row in self.grid)

    def shift_right(self):
        """Shift tiles to the right."""
        self.grid = tuple(_merge_tiles(row[::-1])[::-1] for row in self.grid)

    def shift_up(self):
        """Shift tiles upwards."""
        merged_rows = tuple(_merge_tiles(row) for row in zip(*self.grid))
        self.grid = tuple(zip(*merged_rows))

    def shift_down(self):
        """Shift tiles downwards."""
        merged_rows = [_merge_tiles(row[::-1])[::-1] for row in zip(*self.grid)]
        self.grid = tuple(zip(*merged_rows))


@dataclass
class GameState:
    """Class representing the state of the game."""

    board: GameBoard

    def __init__(self, board: GameBoard | None = None):
        if board is not None:
            self.board = board
        else:
            self.board = GameBoard()

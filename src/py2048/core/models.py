"""Module containing domain models for the 2048 game."""

# pylint: disable=too-few-public-methods

import random
from dataclasses import dataclass

N_ROWS = 4
N_COLS = 4
EMPTY_GRID = tuple(tuple(0 for _ in range(N_COLS)) for _ in range(N_ROWS))


@dataclass(frozen=True)
class GameBoard:
    """Class representing the game board for 2048."""

    grid: tuple[tuple[int, ...], ...] = EMPTY_GRID

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

    def shift_left(self) -> "GameBoard":
        """Shift tiles to the left."""
        return GameBoard(tuple(self._merge_tiles(row) for row in self.grid))

    def shift_right(self):
        """Shift tiles to the right."""
        return GameBoard(tuple(self._merge_tiles(row[::-1])[::-1] for row in self.grid))

    def shift_up(self):
        """Shift tiles upwards."""
        merged_rows = tuple(self._merge_tiles(row) for row in zip(*self.grid))
        return GameBoard(tuple(zip(*merged_rows)))

    def shift_down(self):
        """Shift tiles downwards."""
        merged_rows = [self._merge_tiles(row[::-1])[::-1] for row in zip(*self.grid)]
        return GameBoard(tuple(zip(*merged_rows)))

    def spawn_tile(self) -> "GameBoard":
        """Spawn a new tile on the board."""
        if positions := self.empty_tile_positions:
            i, j = random.choice(positions)
            new_grid = [list(row) for row in self.grid]
            new_grid[i][j] = 2
            return GameBoard(tuple(tuple(row) for row in new_grid))
        raise ValueError("Cannot spawn tile on a full board")

    @staticmethod
    def _merge_tiles(tiles: tuple[int, ...]) -> tuple[int, ...]:
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
        merged_row.extend([0] * (len(tiles) - len(merged_row)))
        return tuple(merged_row)


@dataclass
class GameState:
    """Class representing the state of the game."""

    board: GameBoard = GameBoard()

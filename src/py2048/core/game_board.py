"""Module for the 2048 game board."""

# pylint: disable=too-few-public-methods

import random
from dataclasses import dataclass

GRID_SIZE = 4


@dataclass
class GameBoard:
    """Class representing the game board for 2048."""

    grid: list[list[int]]

    def __init__(self, grid: list[list[int]] | None = None):
        if grid is not None:
            self.grid = grid
        else:
            self.grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
            self._add_random_tile()
            self._add_random_tile()

    def _add_random_tile(self):
        if empty_tiles := [
            (i, j)
            for i in range(GRID_SIZE)
            for j in range(GRID_SIZE)
            if self.grid[i][j] == 0
        ]:
            i, j = random.choice(empty_tiles)
            self.grid[i][j] = 2

    @staticmethod
    def _merge_tiles(tiles: list[int]) -> list[int]:
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
        return merged_row

    def shift_left(self):
        """Shift tiles to the left."""
        for row in self.grid:
            merged_row = self._merge_tiles(row)
            row[:] = merged_row

    def shift_right(self):
        """Shift tiles to the right."""
        for row in self.grid:
            tiles = [tile for tile in row if tile != 0]
            tiles.reverse()
            merged_row = self._merge_tiles(tiles)
            merged_row.reverse()
            row[:] = merged_row

    def shift_up(self):
        """Shift tiles upwards."""
        for col in range(GRID_SIZE):
            column = [self.grid[row][col] for row in range(GRID_SIZE)]
            merged_column = self._merge_tiles(column)
            for row in range(GRID_SIZE):
                self.grid[row][col] = merged_column[row]

    def shift_down(self):
        """Shift tiles downwards."""
        for col in range(GRID_SIZE):
            column = [self.grid[row][col] for row in range(GRID_SIZE)]
            column.reverse()
            merged_column = self._merge_tiles(column)
            merged_column.reverse()
            for row in range(GRID_SIZE):
                self.grid[row][col] = merged_column[row]

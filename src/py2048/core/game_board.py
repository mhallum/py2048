"""Module for the 2048 game board."""

# pylint: disable=too-few-public-methods

import random


class GameBoard:
    """Class representing the game board for 2048."""

    def __init__(self):
        self.grid: list[list[int]] = [[0] * 4 for _ in range(4)]
        self._add_random_tile()
        self._add_random_tile()

    def _add_random_tile(self):
        if empty_tiles := [
            (i, j) for i in range(4) for j in range(4) if self.grid[i][j] == 0
        ]:
            i, j = random.choice(empty_tiles)
            self.grid[i][j] = 2

    def shift_left(self):
        """Shift tiles to the left."""
        for row in self.grid:
            new_row = [tile for tile in row if tile != 0]
            merged_row: list[int] = []
            skip = False
            for i, tile in enumerate(new_row):
                if skip:
                    skip = False
                    continue
                if i < len(new_row) - 1 and tile == new_row[i + 1]:
                    merged_row.append(new_row[i] * 2)
                    skip = True
                else:
                    merged_row.append(new_row[i])
            merged_row.extend([0] * (4 - len(merged_row)))
            row[:] = merged_row

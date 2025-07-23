"""Module for the 2048 game board."""

# pylint: disable=too-few-public-methods

import random


class GameBoard:
    """Class representing the game board for 2048."""

    def __init__(self):
        self.grid = [[0] * 4 for _ in range(4)]
        self._add_random_tile()
        self._add_random_tile()

    def _add_random_tile(self):
        if empty_tiles := [
            (i, j) for i in range(4) for j in range(4) if self.grid[i][j] == 0
        ]:
            i, j = random.choice(empty_tiles)
            self.grid[i][j] = 2

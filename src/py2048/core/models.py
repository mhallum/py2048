"""Module containing domain models for the 2048 game.

This module defines the core data structures used to represent and manipulate
the 2048 game state. It includes:

- `GameBoard`: An immutable 2D grid representing the board, with methods for
  shifting, merging, and spawning tiles according to 2048 rules.
- `GameState`: A higher-level wrapper for managing the overall state of the game,
  such as the current board, and potentially score, game-over status, etc.

Constants:
    N_ROWS (int): Default number of board rows (4).
    N_COLS (int): Default number of board columns (4).
    EMPTY_GRID (tuple[tuple[int, ...], ...]): Predefined empty grid template.
"""

# pylint: disable=too-few-public-methods

from functools import cached_property
import random
from dataclasses import dataclass

N_ROWS = 4
N_COLS = 4
EMPTY_GRID: tuple[tuple[int, ...], ...] = tuple(
    tuple(0 for _ in range(N_COLS)) for _ in range(N_ROWS)
)


@dataclass(frozen=True)
class GameBoard:
    """Immutable representation of a 2048 game board.

    The board is modeled as a 2D tuple of integers, where 0 represents an empty tile.
    All shift and spawn operations return a new GameBoard instance without mutating
    the original.

    Attributes:
        grid (tuple[tuple[int, ...], ...]): A 2D grid of tile values.
    """

    grid: tuple[tuple[int, ...], ...] = EMPTY_GRID

    @cached_property
    def height(self) -> int:
        """Return the number of rows in the game board.

        Returns:
            int: The height of the board, i.e., the number of rows.
        """

        return len(self.grid)

    @cached_property
    def width(self) -> int:
        """Return the number of columns in the game board.

        Returns:
            int: The width of the board, i.e., the number of columns.
        """
        return len(self.grid[0])

    @cached_property
    def empty_tile_positions(self) -> list[tuple[int, int]]:
        """Return the positions of empty tiles on the game board.

        Iterates over the grid and collects all coordinates (row, column) where
        the tile value is 0, indicating an empty space.

        Returns:
            list[tuple[int, int]]: A list of (row, column) positions for all empty tiles.
        """

        return [
            (i, j)
            for i, row in enumerate(self.grid)
            for j, tile in enumerate(row)
            if tile == 0
        ]

    def shift_left(self) -> "GameBoard":
        """Return a new GameBoard with all rows shifted left.

        Each row is processed by moving all non-zero tiles to the left, merging adjacent
        tiles of the same value once per move, and filling the remaining space with zeros.

        Returns:
            GameBoard: A new board instance with tiles shifted and merged to the left.
        """
        return GameBoard(tuple(self._merge_tiles(row) for row in self.grid))

    def shift_right(self) -> "GameBoard":
        """Return a new GameBoard with all rows shifted right.

        Each row is reversed, merged as if shifted left, then reversed again to simulate
        a rightward shift. Adjacent matching tiles merge once per move.

        Returns:
            GameBoard: A new board instance with tiles shifted and merged to the right.
        """

        return GameBoard(tuple(self._merge_tiles(row[::-1])[::-1] for row in self.grid))

    def shift_up(self) -> "GameBoard":
        """Return a new GameBoard with all columns shifted upward.

        Columns are transposed into rows and merged as if shifted left. After merging,
        the result is transposed back to restore column orientation.

        Returns:
            GameBoard: A new board instance with tiles shifted and merged upward.
        """

        merged_rows = tuple(self._merge_tiles(row) for row in zip(*self.grid))
        return GameBoard(tuple(zip(*merged_rows)))

    def shift_down(self) -> "GameBoard":
        """Return a new GameBoard with all columns shifted downward.

        Columns are reversed, merged as if shifted upward, then reversed again to simulate
        a downward shift. Matching tiles merge once per move.

        Returns:
            GameBoard: A new board instance with tiles shifted and merged downward.
        """

        merged_rows = [self._merge_tiles(row[::-1])[::-1] for row in zip(*self.grid)]
        return GameBoard(tuple(zip(*merged_rows)))

    def spawn_tile(self) -> "GameBoard":
        """Return a new GameBoard with a new tile (2) spawned in an empty position.

        A random empty tile is chosen and assigned the value 2.

        Returns:
            GameBoard: A new board instance with the tile added.

        Raises:
            ValueError: If there are no empty positions available to spawn a tile.

        Notes:
            This implementation always spawns a tile with value 2. For authentic 2048 behavior,
            you may optionally spawn a 4 with ~10% probability. This will be implemented
            in a future version.
        """

        if positions := self.empty_tile_positions:
            i, j = random.choice(positions)
            new_grid = [list(row) for row in self.grid]
            new_grid[i][j] = 2
            return GameBoard(tuple(tuple(row) for row in new_grid))
        raise ValueError("Cannot spawn tile on a full board")

    @staticmethod
    def _merge_tiles(tiles: tuple[int, ...]) -> tuple[int, ...]:
        """Merge a single row of tiles to the left, following 2048 rules.

        Consecutive equal non-zero tiles are merged once per move, producing a tile
        of double the value. All non-zero tiles are moved left, and zeros fill the rest.

        Args:
            tiles (tuple[int, ...]): A single row or column of tile values.

        Returns:
            tuple[int, ...]: The merged and left-aligned row, with zeros filling the rest.
        """
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

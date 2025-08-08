"""Game board model for the 2048 game.

This module defines the GameBoard class, an immutable value object representing
a 4x4 grid of tiles. It supports shifting, merging, and spawning tiles in
accordance with 2048 rules. It also includes movement directions and constants
used for spawning behavior.

Classes:
    GameBoard: Represents an immutable grid of tile values and supports all legal operations.
    MoveDirection: Enum representing valid movement directions.

Constants:
    N_ROWS (int): Default number of rows in the game board.
    N_COLS (int): Default number of columns in the game board.
    EMPTY_GRID (tuple): Default empty 4x4 board grid.
    SPAWN_TILE_VALUES (list): Possible values for newly spawned tiles.
    SPAWN_TILE_WEIGHTS (list): Probabilities for spawning tile values.
"""

from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from random import Random

from py2048.core import validators
from py2048.core.exceptions import SpawnTileError

N_ROWS = 4
N_COLS = 4
EMPTY_GRID: tuple[tuple[int, ...], ...] = tuple(
    tuple(0 for _ in range(N_COLS)) for _ in range(N_ROWS)
)
SPAWN_VALUE_4_WEIGHT = 0.1  # Probability of spawning a 4 instead of a 2
SPAWN_TILE_VALUES = [2, 4]
SPAWN_TILE_WEIGHTS = [0.9, 0.1]


class MoveDirection(str, Enum):
    """Enum representing the possible move directions in the game."""

    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


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

    def __post_init__(self):
        """Validate the grid upon initialization."""
        validators.validate_game_board_shape(self)
        validators.validate_game_board_tile_values(self)

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

    @cached_property
    def tile_values(self) -> set[int]:
        """Return a set of all non-zero tile values on the board.

        This property iterates through the grid and collects all unique non-zero
        tile values, which can be useful for game logic that depends on tile values.

        Returns:
            set[int]: A set of unique non-zero tile values present on the board.
        """
        return {tile for row in self.grid for tile in row if tile != 0}

    def get_tile_count(self, tile_value: int) -> int:
        """Return the count of a specific tile value on the board.

        This method counts how many times a given tile value appears in the grid.

        Args:
            tile_value (int): The value of the tile to count.

        Returns:
            int: The number of tiles with the specified value on the board.
        """
        return sum(tile == tile_value for row in self.grid for tile in row)

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

    def spawn_tile(self, rng: Random = Random()) -> "GameBoard":
        """Return a new GameBoard with a new tile (2) spawned in an empty position.

        A random empty tile is chosen and assigned the value 2 or 4 with ~10%
        probability of it being 4.

        Returns:
            GameBoard: A new board instance with the tile added.

        Raises:
            SpawnTileError: If there are no empty positions available to spawn a tile.
        """

        if positions := self.empty_tile_positions:
            i, j = rng.choice(positions)
            new_grid = [list(row) for row in self.grid]
            new_grid[i][j] = rng.choices(SPAWN_TILE_VALUES, weights=SPAWN_TILE_WEIGHTS)[
                0
            ]
            return GameBoard(tuple(tuple(row) for row in new_grid))
        raise SpawnTileError("Cannot spawn tile on a full board")

    @staticmethod
    def _merge_tiles(tiles: tuple[int, ...]) -> tuple[int, ...]:
        """Merge a single row of tiles to the left, following 2048 rules.

        Consecutive equal non-zero tiles are merged once per move, producing a tile
        of double the value. All non-zero tiles are moved left, and zeros fill the rest.

        Args:
            tiles (tuple[int, ...]): A single row or column of tile values.

        Returns:
            tuple[int, ...]: The merged row after applying 2048 merge rules.
        """
        non_zeros = [tile for tile in tiles if tile != 0]
        merged_row: list[int] = []
        skip_next_tile = False
        for i, tile in enumerate(non_zeros):
            if skip_next_tile:  # Skip the next tile if it was already merged
                skip_next_tile = False
                continue
            if i < len(non_zeros) - 1 and tile == non_zeros[i + 1]:  # Merge tiles
                merged_row.append(tile * 2)
                skip_next_tile = True
            else:  # Just add the tile if it wasn't merged
                merged_row.append(tile)
        merged_row.extend([0] * (len(tiles) - len(merged_row)))
        return tuple(merged_row)

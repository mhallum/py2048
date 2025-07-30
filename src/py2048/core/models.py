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

from enum import Enum
from functools import cached_property
import random
from dataclasses import dataclass
from py2048.core import validators
from py2048.core.exceptions import SpawnTileError, InvalidMove

N_ROWS = 4
N_COLS = 4
EMPTY_GRID: tuple[tuple[int, ...], ...] = tuple(
    tuple(0 for _ in range(N_COLS)) for _ in range(N_ROWS)
)


class MoveDirection(Enum):
    """Enum representing the possible move directions in the game."""

    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


def determine_score_from_shifted_board(
    before_board: "GameBoard", shifted_board: "GameBoard"
) -> int:
    """Calculate the score gained from merging tiles during a move.

    Compares the tile counts between the board states before and after a move.
    Assumes merges only occur between identical tiles (2048 rules), and merged
    values must be >= 4 to contribute to score.

    Args:
        before_board (GameBoard): The game board before the move.
        shifted_board (GameBoard): The game board after the move.

    Returns:
        int: The score gained from the move, based on merged tiles.
    """

    before_values = before_board.tile_values
    after_values = shifted_board.tile_values

    # Consider all tile values that appeared in either board
    all_tile_values = sorted(before_values | after_values, reverse=True)

    score = 0
    merged_tile_buffer = 0  # Tracks how many source tiles were consumed by merges

    for value in all_tile_values:
        before_count = before_board.get_tile_count(value) - merged_tile_buffer
        after_count = shifted_board.get_tile_count(value)

        if value >= 4 and after_count > before_count:  # pylint: disable=magic-value-comparison
            # If the tile count increased, it means tiles were merged
            # and the score should be updated accordingly
            score += (after_count - before_count) * value
            # Each new tile of this value comes from two merged tiles
            merged_tile_buffer = (after_count - before_count) * 2
        else:
            # If the tile count did not increase, tiles with value value/2 did not merge
            merged_tile_buffer = 0
    return score


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

    def spawn_tile(self) -> "GameBoard":
        """Return a new GameBoard with a new tile (2) spawned in an empty position.

        A random empty tile is chosen and assigned the value 2.

        Returns:
            GameBoard: A new board instance with the tile added.

        Raises:
            SpawnTileError: If there are no empty positions available to spawn a tile.

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


@dataclass(frozen=True)
class GameState:
    """Class representing the state of the 2048 game.

    Attributes:
        board (GameBoard): The current state of the game board.
        score (int): The current score of the game.

    Properties:
        possible_moves (list[MoveDirection]): Returns a list of directions where moves are possible,
            determined by checking if shifting the board in any direction results in a change.
        is_over (bool): Indicates whether the game is over, which occurs when no moves are possible.
    """

    board: GameBoard = GameBoard()
    score: int = 0

    @cached_property
    def possible_moves(self) -> list[MoveDirection]:
        """Return a list of possible moves based on the current board state.

        Checks if the board can be shifted in any direction (left, right, up, down)
        by attempting to shift and checking if the resulting board is different.

        Returns:
            list[MoveDirection]: A list of directions where moves are possible.
        """
        possible_moves: list[MoveDirection] = []
        for direction in MoveDirection:
            if getattr(self.board, f"shift_{direction.value}")() != self.board:
                possible_moves.append(direction)
        return possible_moves

    @cached_property
    def is_over(self) -> bool:
        """Check if the game is over.

        The game is considered over if there are no possible moves left.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return not self.possible_moves


@dataclass(frozen=True)
class Move:
    """Class representing a move in the game.

    This class encapsulates a single move action, which can be used to
    track the history of moves made during the game.

    Attributes:
        direction (MoveDirection): The direction of the move (e.g., 'left', 'right', 'up', 'down').
    """

    direction: MoveDirection
    before_state: GameState
    after_state: GameState


class Py2048Game:
    """Represents a 2048 game session, including current state and move history.

    The Py2048Game class encapsulates the entire lifecycle of a 2048 game:
    initialization, state updates via player moves, undo functionality, and
    game-over detection.

    Attributes:
        game_id (str): Unique identifier for the game session.
        state (GameState): The current state of the game, including the board and score.
        moves (list[Move]): A chronological history of all valid moves made.

    Properties:
        is_over (bool): Returns True if the game is in a terminal (game-over) state.

    Methods:
        create_new_game(game_id: str) -> Py2048Game:
            Class method to create a new game with two spawned tiles and score set to zero.

        move(direction: MoveDirection) -> None:
            Performs a move in the specified direction, updating the board and score,
            spawning a new tile, and recording the move in history.

        undo_last_move() -> None:
            Reverts the game to the state before the last move, removing the last move
            from the history. Raises an error if no moves have been made.
    """

    def __init__(self, game_id: str, state: GameState, moves: list[Move] | None = None):
        """Initialize the game model with a given state and an optional move history.

        Args:
            state (GameState): The initial state of the game.
            moves (list[Move] | None, optional): History of moves. Defaults to an empty list.
        """
        self.game_id: str = game_id
        self.state: GameState = state
        self.moves: list[Move] = moves if moves is not None else []

    def __hash__(self) -> int:
        """Return a hash of the game instance based on its ID."""
        return hash(self.game_id)

    def __eq__(self, other: object) -> bool:
        """Check equality based on game ID."""
        if not isinstance(other, Py2048Game):
            return False
        return self.game_id == other.game_id

    @property
    def is_over(self) -> bool:
        """Check if the game is over.

        A game is considered over if there are no empty tiles and no possible merges left.
        This is a placeholder implementation; actual logic will be added in future versions.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return self.state.is_over

    @classmethod
    def create_new_game(cls, game_id: str) -> "Py2048Game":
        """Creates and returns a new game.

        This method initializes an empty game board, spawns two tiles at random positions,
        sets the initial score to zero, and returns a new Game object with this state and
        an empty move history.

        Args:
            game_id (str): The unique identifier for the new game.

        Returns:
            Game: A new game instance with two tiles spawned and score set to zero.
        """

        board = GameBoard()  # Initialize with an empty board
        board = board.spawn_tile()  # Spawn the first tile
        board = board.spawn_tile()  # Spawn the second tile
        state = GameState(board=board, score=0)
        return cls(game_id=game_id, state=state, moves=[])

    def move(self, direction: MoveDirection) -> None:
        """Perform a move in the specified direction and update the game state.

        This shifts the board, merges tiles, updates the score, spawns a new tile,
        and records the move in history.

        Args:
            direction (MoveDirection): The direction to move (LEFT, RIGHT, UP, DOWN).

        Raises:
            InvalidMove: If an invalid direction is provided.
        """
        if self.is_over:
            raise InvalidMove("Game is over. No further moves are allowed.")

        current_state = self.state
        board = current_state.board

        match direction:
            case MoveDirection.LEFT:
                shifted_board = board.shift_left()
            case MoveDirection.RIGHT:
                shifted_board = board.shift_right()
            case MoveDirection.UP:
                shifted_board = board.shift_up()
            case MoveDirection.DOWN:
                shifted_board = board.shift_down()

        if shifted_board == self.state.board:
            return

        score_gained = determine_score_from_shifted_board(board, shifted_board)
        updated_score = current_state.score + score_gained

        self.moves.append(
            Move(
                direction=direction,
                before_state=current_state,
                after_state=GameState(board=shifted_board, score=updated_score),
            )
        )

        shifted_board = shifted_board.spawn_tile()

        # Update the game state
        self.state = GameState(board=shifted_board, score=updated_score)

    def undo_last_move(self) -> None:
        """Undo the last move made in the game.

        This method reverts the game state to the state before the last move,
        effectively removing the last action from the game's history.

        Raises:
            ValueError: If there are no moves to undo.
        """
        if not self.moves:
            raise ValueError("No moves to undo.")

        last_move = self.moves.pop()
        self.state = last_move.before_state

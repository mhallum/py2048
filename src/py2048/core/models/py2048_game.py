"""Domain model for managing a single 2048 game session.

This module defines the `Py2048Game` class, which acts as the aggregate root
for the 2048 game domain. It encapsulates the core behaviors and rules of the game,
including board state management, move logic, undo functionality, and domain event generation.

Classes:
    Py2048Game: Represents the lifecycle and state of a single 2048 game session.
"""

from random import Random

from py2048.core import events
from py2048.core.exceptions import InvalidMove

from .game_board import GameBoard, MoveDirection
from .game_state import GameState
from .move import Move
from .scoring import determine_score_from_shifted_board


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

    def __init__(
        self,
        game_id: str,
        state: GameState,
        moves: list[Move] | None = None,
    ):
        """Initialize the game model with a given state and an optional move history.

        Args:
            state (GameState): The initial state of the game.
            moves (list[Move] | None, optional): History of moves. Defaults to an empty list.
        """
        self.game_id: str = game_id
        self.state: GameState = state
        self.moves: list[Move] = moves if moves is not None else []
        self.events: list[events.Event] = []

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
    def create_new_game(cls, game_id: str, rng: Random = Random()) -> "Py2048Game":
        """Creates and returns a new game.

        This method initializes an empty game board, spawns two tiles at random positions,
        sets the initial score to zero, and returns a new Game object with this state and
        an empty move history.

        Args:
            game_id (str): The unique identifier for the new game.
            rng (Random): Random number generator used for spawning initial tiles.

        Returns:
            Game: A new game instance with two tiles spawned and score set to zero.
        """
        board = GameBoard()  # Initialize with an empty board
        board = board.spawn_tile(rng=rng)  # Spawn the first tile
        board = board.spawn_tile(rng=rng)  # Spawn the second tile
        state = GameState(board=board, score=0)
        new_game = cls(game_id=game_id, state=state, moves=[])
        new_game.events.append(events.NewGameStarted(game_id=game_id))
        return new_game

    def move(self, direction: MoveDirection, rng: Random = Random()) -> None:
        """Perform a move in the specified direction and update the game state.

        This shifts the board, merges tiles, updates the score, spawns a new tile,
        and records the move in history.

        Args:
            direction (MoveDirection): The direction to move (LEFT, RIGHT, UP, DOWN).
            rng (Random): Random number generator used for spawning new tiles.

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

        shifted_board = shifted_board.spawn_tile(rng=rng)

        # Update the game state
        self.state = GameState(board=shifted_board, score=updated_score)

        # Check if the game is over after the move
        if self.state.is_over:
            self.events.append(
                events.GameOver(
                    game_id=self.game_id,
                    score=self.state.score,
                    final_grid=self.state.board.grid,
                )
            )

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

"""Integration tests for the game repositories."""

# pylint: disable=too-few-public-methods

from pathlib import Path

from py2048.adapters.repositories import JsonGameRepository
from py2048.core.models import Py2048Game

FAKE_DATA_FOLDER: str = "fake_data_folder"


class TestJsonGameRepository:
    """Test suite for the JsonGameRepository."""

    @staticmethod
    def test_can_add_game(fake_user_data_folder_with_game_1: Path):
        """Test adding and retrieving a game from the JSON repository."""
        game = Py2048Game.create_new_game(slot_id="test_slot_1")
        repository = JsonGameRepository(folder=fake_user_data_folder_with_game_1)
        repository.add(game)

        retrieved_game = repository.get("test_slot_1")
        assert retrieved_game == game

    # This used to raise an error, but now it should not
    # because I want to leave the handling of missing games to the caller.
    @staticmethod
    def test_get_non_existent_game_returns_none(
        fake_user_data_folder_with_game_1: Path,
    ):
        """Test that trying to get a non-existent game returns None."""
        repository = JsonGameRepository(folder=fake_user_data_folder_with_game_1)
        result = repository.get("non_existent")
        assert result is None

    @staticmethod
    def test_can_get_existing_game(fake_user_data_folder_with_game_1: Path):
        """Test retrieving an existing game from the JSON repository."""
        repository = JsonGameRepository(folder=fake_user_data_folder_with_game_1)
        slot_id = "current_game"
        game = repository.get(slot_id)
        assert isinstance(game, Py2048Game)
        assert game.slot_id == slot_id
        assert game.state.board.grid == (
            (0, 0, 0, 0),
            (0, 0, 2, 0),
            (0, 0, 0, 4),
            (0, 0, 4, 2),
        )
        expected_score = 8
        assert game.state.score == expected_score
        expected_num_moves = 4
        assert len(game.moves) == expected_num_moves

    @staticmethod
    def test_missing_file_does_not_raise_error(fake_user_data_folder: Path):
        """Test that missing JSON file does not raise an error on initialization.

        Instead it initializes an empty repository.
        """
        repository = JsonGameRepository(folder=fake_user_data_folder)
        assert isinstance(repository, JsonGameRepository)
        assert len(repository.list()) == 0

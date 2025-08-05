"""Integration tests for the game repositories."""

# pylint: disable=too-few-public-methods

from pathlib import Path

import pytest

from py2048.adapters.repositories import JsonGameRepository
from py2048.core.models import Py2048Game

FAKE_DATA_FOLDER: str = "fake_data_folder"


class TestJsonGameRepository:
    """Test suite for the JsonGameRepository."""

    @staticmethod
    def test_can_add_game(fake_user_data_folder_with_game_1: Path):
        """Test adding and retrieving a game from the JSON repository."""
        game = Py2048Game.create_new_game(game_id="test_new_game")
        repository = JsonGameRepository(folder=fake_user_data_folder_with_game_1)
        repository.add(game)

        retrieved_game = repository.get("test_new_game")
        assert retrieved_game == game

    @staticmethod
    def test_get_non_existent_game_raises_error(
        fake_user_data_folder_with_game_1: Path,
    ):
        """Test that trying to get a non-existent game raises a KeyError."""
        repository = JsonGameRepository(folder=fake_user_data_folder_with_game_1)
        with pytest.raises(
            KeyError, match="Game with ID non_existent not found in repository."
        ):
            repository.get("non_existent")

    @staticmethod
    def test_can_get_existing_game(fake_user_data_folder_with_game_1: Path):
        """Test retrieving an existing game from the JSON repository."""
        repository = JsonGameRepository(folder=fake_user_data_folder_with_game_1)
        game_id = "current_game"
        game = repository.get(game_id)
        assert isinstance(game, Py2048Game)
        assert game.game_id == game_id
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

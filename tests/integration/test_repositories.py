"""Integration tests for the game repositories."""

# pylint: disable=too-few-public-methods

import pytest
from py2048.adapters.repositories import InMemoryGameRepository
from py2048.core.models import Py2048Game


class TestInMemoryGameRepository:
    """Test suite for the InMemoryGameRepository."""

    @staticmethod
    def test_can_add_game():
        """Test adding a game to the repository."""
        game = Py2048Game.create_new_game(game_id="test_game")
        repository = InMemoryGameRepository()
        repository.add(game)

        retrieved_game = repository.get("test_game")
        assert retrieved_game == game

    @staticmethod
    def test_can_get_game_by_id():
        """Test retrieving a game by its ID."""
        repository = InMemoryGameRepository()
        game1 = Py2048Game.create_new_game(game_id="test_game1")
        game2 = Py2048Game.create_new_game(game_id="test_game2")
        repository.add(game1)
        repository.add(game2)

        retrieved_game = repository.get("test_game1")
        assert retrieved_game == game1

    @staticmethod
    def test_get_non_existent_game_raises_error():
        """Test that trying to get a non-existent game raises a KeyError."""
        repository = InMemoryGameRepository()
        with pytest.raises(
            KeyError, match="Game with ID non_existent not found in repository."
        ):
            repository.get("non_existent")

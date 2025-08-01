"""Test suite for the game_screen_values view in the Py2048 application."""

from py2048 import bootstrap, views
from py2048.core import models  # for type hinting


def test_game_screen_values_view(test_game: "models.Py2048Game"):
    """Test the game_screen_values view."""
    bus = bootstrap.bootstrap()
    bus.uow.games.add(test_game)
    game_id = test_game.game_id

    screen_values = views.game_screen_values(game_id, uow=bus.uow)

    assert screen_values["board"] == test_game.state.board.grid
    assert screen_values["score"] == test_game.state.score
    assert (
        screen_values["high_score"] == 0
    )  # Placeholder, high score logic not implemented yet

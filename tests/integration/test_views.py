"""Test suite for the game_screen_values view in the Py2048 application."""

from pathlib import Path

from py2048 import bootstrap, views
from py2048.service_layer.unit_of_work import JsonUnitOfWork


def test_game_screen_values_view(fake_user_data_folder_with_game: Path):
    """Test the game_screen_values view."""
    bus = bootstrap.bootstrap(JsonUnitOfWork(fake_user_data_folder_with_game))

    screen_values = views.game_screen_values("test_game", uow=bus.uow)

    expected_grid = (
        (4, 2, 0, 0),
        (0, 0, 0, 0),
        (0, 0, 0, 0),
        (0, 0, 0, 0),
    )

    expected_score = 4

    assert screen_values["board"] == expected_grid
    assert screen_values["score"] == expected_score
    assert (
        screen_values["high_score"] == 0
    )  # Placeholder, high score logic not implemented yet

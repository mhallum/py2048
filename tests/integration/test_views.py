"""Test suite for the game_screen_values view in the Py2048 application."""

from pathlib import Path

from py2048 import bootstrap, views
from py2048.service_layer.unit_of_work import JsonUnitOfWork


def test_game_screen_values_view(fake_user_data_folder_with_game_1: Path):
    """Test the game_screen_values view."""
    bus = bootstrap.bootstrap(JsonUnitOfWork(fake_user_data_folder_with_game_1))

    screen_values = views.game_screen_values("current_game", uow=bus.uow)

    expected_grid = (
        (0, 0, 0, 0),
        (0, 0, 2, 0),
        (0, 0, 0, 4),
        (0, 0, 4, 2),
    )

    expected_score = 8

    assert screen_values["grid"] == expected_grid
    assert screen_values["score"] == expected_score
    assert (
        screen_values["high_score"] == 0
    )  # Placeholder, high score logic not implemented yet

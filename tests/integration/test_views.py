"""Test suite for the game_screen_values view in the Py2048 application."""

from pathlib import Path

from py2048 import bootstrap, views
from py2048.service_layer.unit_of_work import JsonUnitOfWork


def test_game_screen_values_view(fake_user_data_folder_with_game_1: Path):
    """Test the game_screen_values view."""
    bus = bootstrap.bootstrap(JsonUnitOfWork(fake_user_data_folder_with_game_1))

    screen_values = views.query_game_screen_values_by_slot("current_game", uow=bus.uow)

    expected_grid = (
        (0, 0, 0, 0),
        (0, 0, 2, 0),
        (0, 0, 0, 4),
        (0, 0, 4, 2),
    )

    expected_score = 8

    assert screen_values is not None
    assert screen_values.grid == expected_grid
    assert screen_values.score == expected_score
    assert (
        screen_values.high_score == 0
    )  # Placeholder, high score logic not implemented yet


def test_high_score_query(fake_user_data_folder_with_records_file: Path):
    """Test the high score query."""
    bus = bootstrap.bootstrap(JsonUnitOfWork(fake_user_data_folder_with_records_file))

    high_score = views.query_high_score(bus.uow)

    expected_high_score = 200
    assert high_score == expected_high_score, (
        f"High score should be {expected_high_score} but got {high_score}"
    )


def test_final_score_query(fake_user_data_folder_with_records_file: Path):
    """Test the final score query."""
    bus = bootstrap.bootstrap(JsonUnitOfWork(fake_user_data_folder_with_records_file))

    final_score = views.final_score_query(uow=bus.uow, game_uuid="test_uuid_1")

    expected_final_score = 100
    assert final_score == expected_final_score, (
        f"Final score should be {expected_final_score} but got {final_score}"
    )


def test_final_score_query_non_existent_game(
    fake_user_data_folder_with_records_file: Path,
):
    """Test the final score query for a non-existent game."""
    bus = bootstrap.bootstrap(JsonUnitOfWork(fake_user_data_folder_with_records_file))

    final_score = views.final_score_query(uow=bus.uow, game_uuid="non_existent")

    assert final_score is None, "Final score for non-existent game should be None"

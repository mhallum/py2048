"""Functional tests for the TUI interface of Py2048."""

from pathlib import Path
from random import Random
from typing import cast

import pytest

from py2048.bootstrap import bootstrap
from py2048.interfaces.tui.app import Py2048TUIApp
from py2048.interfaces.tui.screens import GameScreen, MainMenu
from py2048.service_layer.messagebus import MessageBus
from py2048.service_layer.unit_of_work import JsonUnitOfWork


def bootstrap_test_app(path: Path) -> MessageBus:
    """Bootstrap the application with a new MessageBus."""
    return bootstrap(
        uow=JsonUnitOfWork(path), rng=Random(42)
    )  # RNG is seeded with Random(42); this makes tile spawns deterministic.


def get_game_screen(app: Py2048TUIApp) -> GameScreen:
    """Get the GameScreen instance from the app."""
    return cast(GameScreen, app.get_screen("game"))  # type: ignore


def get_main_menu_screen(app: Py2048TUIApp) -> GameScreen:
    """Get the MainMenu instance from the app."""
    return cast(MainMenu, app.get_screen("main_menu"))  # type: ignore


@pytest.mark.functional
@pytest.mark.asyncio
async def test_playing_new_game(
    fake_styles_folder_populated: Path, fake_user_data_folder: Path
) -> None:
    """Test selecting 'New Game' in the main menu."""

    # Ensure CSS file is available
    css_path: Path = fake_styles_folder_populated.joinpath("game_screen.tcss")
    assert css_path.is_file(), "CSS file should exist at the specified path."

    # Bootstrap test app with fake data directory
    bus = bootstrap_test_app(fake_user_data_folder)
    # RNG is seeded with Random(42); this makes tile spawns deterministic.

    app = Py2048TUIApp(bus=bus)

    async with app.run_test() as pilot:
        # The user is presented with the main menu
        assert get_main_menu_screen(app).is_active

        # The user selects 'New Game'
        await pilot.press("enter")

        # The game screen is now displayed
        assert get_game_screen(app).is_active

        # The user can see a game board with two spawned tiles
        assert get_game_screen(app).board.grid == (
            (0, 0, 0, 2),
            (0, 2, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        )
        # The user can see the score board with initial score 0
        assert get_game_screen(app).scores.score == 0
        # The user can see the high score board with initial high score 0
        assert get_game_screen(app).scores.high_score == 0

        # The user moves up
        await pilot.press("up")

        # The game board is updated with the new state after the move
        assert get_game_screen(app).board.grid == (
            (0, 2, 0, 2),
            (2, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        )  # a new tile is spawned after the move
        # The score is updated after the move
        assert (
            get_game_screen(app).scores.score == 0
        )  # no score change since no tiles merged
        # The high score remains unchanged
        assert get_game_screen(app).scores.high_score == 0

        # The user moves down
        await pilot.press("down")

        # The game board is updated with the new state after the move
        assert get_game_screen(app).board.grid == (
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 2, 0),
            (2, 2, 0, 2),
        )  # The board has shifted down and spawned a new tile
        # The score is updated after the move
        assert (
            get_game_screen(app).scores.score == 0
        )  # no score change since no tiles merged
        # The high score remains unchanged
        assert get_game_screen(app).scores.high_score == 0

        # The user moves left
        await pilot.press("left")

        # The game board is updated with the new state after the move
        assert get_game_screen(app).board.grid == (
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (2, 2, 0, 0),
            (4, 2, 0, 0),
        )
        # The board has shifted left (merging the 2s) and spawned a new tile
        # The score is updated after the move
        expected_score = 4  # score increased by 4 from merging tiles
        assert (
            get_game_screen(app).scores.score == expected_score
        )  # score increased by 4 from merging tiles
        # The high score remains unchanged
        assert get_game_screen(app).scores.high_score == 0

        # the user moves right
        await pilot.press("right")

        # The game board is updated with the new state after the move
        assert get_game_screen(app).board.grid == (
            (0, 0, 0, 0),
            (0, 0, 2, 0),
            (0, 0, 0, 4),
            (0, 0, 4, 2),
        )  # The board has shifted right (merging the 2s) and spawned a new tile
        # The score is updated after the move
        expected_score = 8  # score increased by 4 from merging tiles
        assert get_game_screen(app).scores.score == expected_score
        # The high score remains unchanged
        assert get_game_screen(app).scores.high_score == 0

        # The user decides to quit the game
        await pilot.press("q")

        # The user is back in the main menu
        assert get_main_menu_screen(app).is_active

        # The user quits the game
        await pilot.press("q")

        # The app exits cleanly
        assert app.is_running is False


@pytest.mark.functional
@pytest.mark.asyncio
async def test_resuming_game(
    fake_styles_folder_populated: Path, fake_user_data_folder_with_game_1: Path
) -> None:
    """Test selecting 'New Game' in the main menu."""

    # Ensure CSS file is available
    css_path: Path = fake_styles_folder_populated.joinpath("game_screen.tcss")
    assert css_path.is_file(), "CSS file should exist at the specified path."

    # Bootstrap test app with fake data directory
    bus = bootstrap_test_app(fake_user_data_folder_with_game_1)
    # RNG is seeded with Random(42); this makes tile spawns deterministic.

    app = Py2048TUIApp(bus=bus)

    async with app.run_test() as pilot:
        # The user is presented with the main menu
        assert get_main_menu_screen(app).is_active

        # The user selects "Resume Game"
        await pilot.press("down")
        await pilot.press("enter")

        # The user is now seeing the game screen
        assert get_game_screen(app).is_active

        # The user can see a game board with the state from the saved game
        assert get_game_screen(app).board.grid == (
            (0, 0, 0, 0),
            (0, 0, 2, 0),
            (0, 0, 0, 4),
            (0, 0, 4, 2),
        )
        # The user can see the score board with the score from the saved game
        expected_score = 8  # score from the saved game
        assert get_game_screen(app).scores.score == expected_score
        # The user can see the high score board with the high score from the saved game
        assert get_game_screen(app).scores.high_score == 0

        # The user decides to finish the game another day.
        await pilot.press("q")
        await pilot.press("q")
        assert app.is_running is False

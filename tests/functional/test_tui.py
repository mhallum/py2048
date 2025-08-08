"""Functional tests for the TUI interface of Py2048."""

from pathlib import Path
from random import Random
from typing import cast

import pytest
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from py2048.bootstrap import bootstrap
from py2048.interfaces.tui.app import Py2048TUIApp
from py2048.interfaces.tui.screens import GameOverScreen, GameScreen, MainMenu
from py2048.service_layer.messagebus import MessageBus
from py2048.service_layer.unit_of_work import JsonUnitOfWork


def bootstrap_test_app(path: Path) -> MessageBus:
    """Bootstrap the application with a new MessageBus."""
    return bootstrap(
        uow=JsonUnitOfWork(path), rng=Random(42)
    )  # RNG is seeded with Random(42); this makes tile spawns deterministic.


def get_main_menu_screen(app: Py2048TUIApp) -> MainMenu:
    """Get the MainMenu instance from the app."""
    return cast(MainMenu, app.get_screen("main_menu"))  # type: ignore


def get_displayed_score(app: Py2048TUIApp) -> int:
    """Get the score displayed in the app."""
    if not isinstance(app.screen, GameScreen):
        raise ValueError("Current screen is not a GameScreen.")
    return int(app.screen.query_one("#current-score #value-part").renderable)  # type: ignore


def get_displayed_high_score(app: Py2048TUIApp) -> int:
    """Get the high score displayed in the app."""
    if not isinstance(app.screen, GameScreen):
        raise ValueError("Current screen is not a GameScreen.")
    return int(app.screen.query_one("#high-score #value-part").renderable)  # type: ignore


def get_resume_game_option(app: Py2048TUIApp) -> Option:
    """Get the 'Resume Game' option from the main menu."""
    option_list = app.screen.query_one("#main-menu-options", OptionList)
    resume_game_id = "resume-game"
    for option in option_list.options:
        if option.id == resume_game_id:
            return option
    raise ValueError("Resume Game option not found in the main menu.")


@pytest.mark.functional
@pytest.mark.asyncio
async def test_playing_new_game(
    fake_styles_folder_populated: Path, fake_user_data_folder: Path
) -> None:
    """Test selecting 'New Game' in the main menu."""

    ## Ensure CSS file is available
    css_path: Path = fake_styles_folder_populated.joinpath("game_screen.tcss")
    assert css_path.is_file(), "CSS file should exist at the specified path."

    ## Bootstrap test app with fake data directory
    bus = bootstrap_test_app(fake_user_data_folder)
    ## RNG is seeded with Random(42); this makes tile spawns deterministic.

    app = Py2048TUIApp(bus=bus)

    async with app.run_test() as pilot:
        # The user is presented with the main menu
        assert get_main_menu_screen(app).is_active

        # The user sees the welcome message
        welcome_message = "Welcome to Py2048!"
        assert (
            app.screen.query_one("#welcome-label").renderable  # type: ignore
            == welcome_message
        )  # type: ignore

        # The user sees the main menu title
        main_menu_title = "Main Menu"
        assert (
            app.screen.query_one("#main-menu-title").renderable  # type: ignore
            == main_menu_title
        )

        # The user sees that "Resume Game" is disabled
        assert get_resume_game_option(app).disabled is True

        # The user selects 'New Game'
        await pilot.press("enter")

        # The game screen is now displayed
        assert isinstance(app.screen, GameScreen)

        # The user can see a game board with two spawned tiles
        assert app.screen.board.grid == (
            (0, 0, 0, 2),
            (0, 2, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        )
        # The user can see the score board with initial score 0
        assert get_displayed_score(app) == 0
        # The user can see the high score board with initial high score 0
        assert get_displayed_high_score(app) == 0

        # The user moves up
        await pilot.press("up")

        # The game board is updated with the new state after the move
        assert app.screen.board.grid == (
            (0, 2, 0, 2),
            (2, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        )  # a new tile is spawned after the move
        # The score is updated after the move
        assert get_displayed_score(app) == 0  # no score change since no tiles merged
        # The high score remains unchanged
        assert get_displayed_high_score(app) == 0

        # The user moves down
        await pilot.press("down")

        # The game board is updated with the new state after the move
        assert app.screen.board.grid == (
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 2, 0),
            (2, 2, 0, 2),
        )  # The board has shifted down and spawned a new tile
        # The score is updated after the move
        assert get_displayed_score(app) == 0  # no score change since no tiles merged
        # The high score remains unchanged
        assert get_displayed_high_score(app) == 0

        # The user moves left
        await pilot.press("left")

        # The game board is updated with the new state after the move
        assert app.screen.board.grid == (
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (2, 2, 0, 0),
            (4, 2, 0, 0),
        )
        # The board has shifted left (merging the 2s) and spawned a new tile
        # The score is updated after the move
        expected_score = 4  # score increased by 4 from merging tiles
        assert get_displayed_score(app) == expected_score
        # The high score remains unchanged
        assert get_displayed_high_score(app) == 0

        # the user moves right
        await pilot.press("right")

        # The game board is updated with the new state after the move
        assert app.screen.board.grid == (
            (0, 0, 0, 0),
            (0, 0, 2, 0),
            (0, 0, 0, 4),
            (0, 0, 4, 2),
        )  # The board has shifted right (merging the 2s) and spawned a new tile
        # The score is updated after the move
        expected_score = 8  # score increased by 4 from merging tiles
        assert get_displayed_score(app) == expected_score

        # The high score remains unchanged
        assert app.screen.query_one("#high-score #value-part").renderable == str(  # type: ignore
            0
        )

        # The user decides to quit the game
        await pilot.press("q")

        # The user is back in the main menu
        assert get_main_menu_screen(app).is_active

        # The user sees that "Resume Game" is now enabled
        assert get_resume_game_option(app).disabled is False

        # The user navigates to "Exit" and selects it
        await pilot.press("down")
        await pilot.press("down")
        await pilot.press("enter")

        # The app exits cleanly
        assert app.is_running is False


@pytest.mark.functional
@pytest.mark.asyncio
async def test_resuming_game(
    fake_styles_folder_populated: Path, fake_user_data_folder_with_game_1: Path
) -> None:
    """Test selecting 'New Game' in the main menu."""

    ## Ensure CSS file is available
    css_path: Path = fake_styles_folder_populated.joinpath("game_screen.tcss")
    assert css_path.is_file(), "CSS file should exist at the specified path."

    ## Bootstrap test app with fake data directory
    bus = bootstrap_test_app(fake_user_data_folder_with_game_1)
    ## RNG is seeded with Random(42); this makes tile spawns deterministic.

    app = Py2048TUIApp(bus=bus)

    async with app.run_test() as pilot:
        # The user is presented with the main menu
        assert get_main_menu_screen(app).is_active

        # The user selects "Resume Game"
        await pilot.press("down")
        await pilot.press("enter")

        # The user is now seeing the game screen
        assert isinstance(app.screen, GameScreen)

        # The user can see a game board with the state from the saved game
        assert app.screen.board.grid == (
            (0, 0, 0, 0),
            (0, 0, 2, 0),
            (0, 0, 0, 4),
            (0, 0, 4, 2),
        )
        # The user can see the score board with the score from the saved game
        expected_score = 8  ## score from the saved game
        assert get_displayed_score(app) == expected_score
        # The user can see the high score board with the high score from the saved game
        assert get_displayed_high_score(app) == 0

        # The user decides to finish the game another day.
        await pilot.press("q")
        await pilot.press("q")
        assert app.is_running is False


@pytest.mark.functional
@pytest.mark.asyncio
async def test_finishing_game(
    fake_styles_folder_populated: Path, fake_user_data_folder_with_game_2: Path
) -> None:
    """Test finishing a game and returning to the main menu."""

    ## Ensure CSS file is available
    css_path: Path = fake_styles_folder_populated.joinpath("game_screen.tcss")
    assert css_path.is_file(), "CSS file should exist at the specified path."

    ## Bootstrap test app with fake data directory
    ## This folder fixture contains a game that is almost finished
    ## The game is set up so that the user can finish it in a few moves
    bus = bootstrap_test_app(fake_user_data_folder_with_game_2)
    app = Py2048TUIApp(bus=bus)

    # The user has been playing the game in their off time and has finally decided to finish a game
    async with app.run_test() as pilot:
        # The user is presented with the main menu
        assert get_main_menu_screen(app).is_active

        # The user selects "Resume Game"
        await pilot.press("down")
        await pilot.press("enter")

        # The user is now seeing the game screen
        assert app.screen.is_active

        # The user makes the last move to finish the game
        await pilot.press("up")

        # The user is now viewing the game over screen
        assert isinstance(app.screen, GameOverScreen)

        # The user sees a message indicating the game is over
        game_over_message = "GAME OVER!"
        assert (
            app.screen.get_child_by_id("game-over-title").renderable  # type: ignore
            == game_over_message
        )

        # The user can see the final score
        expected_final_score = 1716
        assert app.screen.query_one("#final-score #value-part").renderable == str(  # type: ignore
            expected_final_score
        )

        # The user presses a key to return to the main menu
        await pilot.press("enter")

        # The user is back in the main menu
        assert get_main_menu_screen(app).is_active

        # The user sees that "Resume Game" is now disabled
        assert get_resume_game_option(app).disabled is True, (
            "Resume Game option should be disabled after finishing the game, but it is not."
        )

        # The user decides to quit the game
        await pilot.press("q")

        # The app exits cleanly
        assert app.is_running is False

"""Functional tests for the CLI of Py2048."""

from pathlib import Path
from random import Random
from unittest.mock import MagicMock, patch

import pytest
from blessed import Terminal
from blessed.keyboard import Keystroke
from pytest import CaptureFixture
from rich.console import Console

from py2048.bootstrap import bootstrap
from py2048.interfaces.cli.game_screen import GameScreen
from py2048.interfaces.cli.main import run_cli
from py2048.interfaces.cli.runners import LOOP_TERMINATION_DELIMITER, DisplayIO
from py2048.service_layer.unit_of_work import JsonUnitOfWork

KEY_UP = 259
KEY_DOWN = 258
KEY_LEFT = 260
KEY_RIGHT = 261
KEY_ENTER = 343
KEY_ESCAPE = 27

TITLE_MARKER = "Welcome to Py2048!"  # Expected title in the CLI menu
EXIT_MESSAGE = "Goodbye!"  # Expected message when exiting the CLI
EXIT_MENU_ITEM = "Exit"  # Expected exit menu item
NEW_GAME_MENU_ITEM = "New Game"  # Expected new game menu item


def fake_key(code: int, name: str) -> MagicMock:
    """Create a mock key press."""
    key = MagicMock()
    key.code = code
    key.name = name
    return key


def split_console_output_loops(
    output: str, loop_termination_delimiter: str
) -> list[str]:
    """Splits the console output by loop"""
    return output.split(loop_termination_delimiter)


@pytest.mark.functional
def test_running_cli_opens_main_menu(
    fake_user_data_folder: Path, capsys: CaptureFixture[str]
):
    """Test that running the CLI opens the main menu."""
    display = DisplayIO(
        term=Terminal(),
        console=Console(record=True),
    )
    bus = bootstrap(uow=JsonUnitOfWork(fake_user_data_folder))
    with patch.object(
        display.term,
        "inkey",
        side_effect=[
            fake_key(KEY_DOWN, "KEY_DOWN"),  # User presses down to select Exit
            fake_key(KEY_ENTER, "KEY_ENTER"),  # User presses enter (selected Exit)
        ],
    ):
        # Run the CLI interface
        run_cli(bus=bus, display=display)
        captured = capsys.readouterr()

    # Menu title is displayed
    assert TITLE_MARKER in captured.out

    # New Game is the first item and is highlighted
    assert "➤ " + NEW_GAME_MENU_ITEM in captured.out

    # Exit is the second item
    assert EXIT_MENU_ITEM in captured.out


@pytest.mark.functional
def test_menu_navigation(fake_user_data_folder: Path):
    """Test that the menu can be navigated using arrow keys."""
    bus = bootstrap(uow=JsonUnitOfWork(Path(fake_user_data_folder)))
    display = DisplayIO(term=Terminal(), console=Console(record=True))

    # The user experiments with the menu controls
    with patch.object(
        display.term,
        "inkey",
        side_effect=[
            fake_key(KEY_DOWN, "KEY_DOWN"),  # User presses down (Exit is selected)
            fake_key(KEY_UP, "KEY_UP"),  # User presses up (New Game is selected)
            fake_key(KEY_DOWN, "KEY_DOWN"),  # User presses down again
            fake_key(KEY_ENTER, "KEY_ENTER"),  # User presses enter (selected Exit)
        ],
    ):
        # Run the CLI interface
        run_cli(bus=bus, display=display, test_mode=True)
        raw_output = display.console.export_text()

    loops = split_console_output_loops(raw_output, LOOP_TERMINATION_DELIMITER)

    # Check output after user opens the menu
    assert "➤ " + NEW_GAME_MENU_ITEM in loops[0]
    assert "➤ " + EXIT_MENU_ITEM not in loops[0]

    # Check output after User presses down
    assert "➤ " + EXIT_MENU_ITEM in loops[1]
    assert "➤ " + NEW_GAME_MENU_ITEM not in loops[1]

    # Check output after User presses up
    assert "➤ " + NEW_GAME_MENU_ITEM in loops[2]
    assert "➤ " + EXIT_MENU_ITEM not in loops[2]

    # Check output after User presses down again
    assert "➤ " + EXIT_MENU_ITEM in loops[3]
    assert "➤ " + NEW_GAME_MENU_ITEM not in loops[3]

    # Check output after User presses enter
    assert EXIT_MESSAGE in loops[4]


@pytest.mark.functional
def test_starting_a_new_game(fake_user_data_folder: Path):
    """Test that selecting 'New Game' opens a game screen with a fresh game."""
    term = Terminal()
    console = Console(record=True)
    display = DisplayIO(term=term, console=console)
    bus = bootstrap(
        uow=JsonUnitOfWork(Path(fake_user_data_folder)), rng=Random(42)
    )  # Using a fixed seed to make the game state predictable

    side_effects: list[MagicMock | Keystroke] = []

    # The user is in the main menu and selects 'New Game'
    side_effects.append(fake_key(KEY_ENTER, "KEY_ENTER"))
    # The user should now be viewing the game screen with a fresh game
    # (see assertions: 1)

    # The user moves up
    side_effects.append(fake_key(KEY_UP, "KEY_UP"))
    # The user should now be viewing the an updated game screen with the move applied
    # (see assertions: 2)

    # The user moves down
    side_effects.append(fake_key(KEY_DOWN, "KEY_DOWN"))
    # The user should now be viewing the an updated game screen with the move applied
    # (see assertions: 3)

    # The user moves left
    side_effects.append(fake_key(KEY_LEFT, "KEY_LEFT"))
    # The user should now be viewing the an updated game screen with the move applied
    # (see assertions: 4)

    # The user moves right
    side_effects.append(fake_key(KEY_RIGHT, "KEY_RIGHT"))
    # The user should now be viewing the an updated game screen with the move applied
    # (see assertions: 5)

    # The user exits the game
    side_effects.append(Keystroke("q"))
    #  A goodbye message should be displayed
    # (see assertions: 6)

    with patch.object(term, "inkey", side_effect=side_effects):
        run_cli(bus=bus, display=display, test_mode=True)
        raw_output = console.export_text()
    loops = split_console_output_loops(raw_output, LOOP_TERMINATION_DELIMITER)[
        0:-1
    ]  # Exclude the last empty loop

    expected_number_of_loops = 6
    assert len(loops) == expected_number_of_loops

    # Assertions for the 1st game loop (New Game)
    expected_game_screen = GameScreen(
        grid=((0, 0, 0, 2), (0, 2, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
        score=0,
        high_score=0,
    )  # Game starts with 2 spawned tiles
    game_screen = GameScreen.from_output(loops[1])
    assert game_screen == expected_game_screen

    # Assertions for the second loop (after moving up)
    expected_game_screen = GameScreen(
        grid=((0, 2, 0, 2), (2, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
        score=0,
        high_score=0,
    )  # The board has shifted up and spawned a new tile
    game_screen = GameScreen.from_output(loops[2])
    assert game_screen == expected_game_screen

    # Assertions for the third loop (after moving down)
    expected_game_screen = GameScreen(
        grid=((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 2, 0), (2, 2, 0, 2)),
        score=0,
        high_score=0,
    )  # The board has shifted down and spawned a new tile
    game_screen = GameScreen.from_output(loops[3])
    assert game_screen == expected_game_screen

    # Assertions for the fourth loop (after moving left)
    expected_game_screen = GameScreen(
        grid=((0, 0, 0, 0), (0, 0, 0, 0), (2, 2, 0, 0), (4, 2, 0, 0)),
        score=4,  # Score should be 4 after merging two 2s
        high_score=0,
    )  # The board has shifted left (merging the 2s) and spawned a new tile
    game_screen = GameScreen.from_output(loops[4])
    assert game_screen == expected_game_screen

    # Assertions for the fifth loop (after moving right)
    expected_game_screen = GameScreen(
        grid=((0, 0, 0, 0), (0, 0, 2, 0), (0, 0, 0, 4), (0, 0, 4, 2)),
        score=8,  # Score should increase by 4 after merging two 2s
        high_score=0,
    )  # The board has shifted right (merging the 2s) and spawned a new tile
    game_screen = GameScreen.from_output(loops[5])
    assert game_screen == expected_game_screen

    # A goodbye message should be displayed after the user exits
    assert EXIT_MESSAGE in loops[5]


# Add test for other key presses
# Add test for invalid moves
# Add test for undo functionality

# test_resuming_game

# test_starting_another_game

# test_finishing_game

# test_starting_another_game_after_finishing

# test_viewing_statistics
# test_resetting_statistics

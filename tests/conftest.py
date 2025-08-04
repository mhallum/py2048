"""pytest configuration file for the py2048 project."""

from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from py2048.core import models


@pytest.fixture
def fake_user_data_folder(fs: FakeFilesystem) -> Path:
    """Fixture to provide a fake user data folder for testing."""
    path = Path("fake_user_data_folder")
    fs.create_dir(str(path))  # type: ignore
    return path


@pytest.fixture
def fake_user_data_folder_with_game(
    fs: FakeFilesystem,
    fake_user_data_folder: Path,  # pylint: disable=redefined-outer-name
) -> Path:
    """Fixture to provide a fake data folder for testing with pyfakefs."""

    test_json = """[
        {
            "game_id": "test_game",
            "state": {
                "board": {
                    "grid": [
                        [4, 2, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0]
                    ]
                },
                "score": 4
            },
            "moves": [
                {
                    "direction": "LEFT",
                    "before_state": {
                        "board": {
                            "grid": [
                                [0, 2, 2, 0],
                                [0, 0, 0, 0],
                                [0, 0, 0, 0],
                                [0, 0, 0, 0]
                            ]
                        },
                        "score": 0
                    },
                    "after_state": {
                        "board": {
                            "grid": [
                                [4, 0, 0, 0],
                                [0, 0, 0, 0],
                                [0, 0, 0, 0],
                                [0, 0, 0, 0]
                            ]
                        },
                        "score": 4
                    }
                }
            ]
        }
    ]"""

    games_file = fake_user_data_folder / "games.json"  # type: ignore
    fs.create_file(str(games_file), contents=test_json)  # type: ignore

    return fake_user_data_folder


@pytest.fixture
def test_game() -> models.Py2048Game:
    """Fixture to create a test game instance."""
    board = models.GameBoard(
        grid=((0, 0, 2, 0), (0, 0, 0, 0), (0, 0, 2, 0), (0, 0, 0, 0))
    )
    state = models.GameState(board=board, score=0)
    return models.Py2048Game(game_id="test_game", state=state)

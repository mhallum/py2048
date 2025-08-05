"""pytest configuration file for the py2048 project."""

from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from py2048.core import models


def load_fake_game_data(filename: str) -> str:
    """Load test game data from a JSON file."""

    path = Path(__file__).parent / "data" / filename
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


fake_game_data_1 = load_fake_game_data("test_game_1.json")
fake_game_data_2 = load_fake_game_data("test_game_2.json")


@pytest.fixture
def fake_user_data_folder(fs: FakeFilesystem) -> Path:
    """Fixture to provide a fake user data folder for testing."""
    path = Path("fake_user_data_folder")
    fs.create_dir(str(path))  # type: ignore
    return path


@pytest.fixture
def fake_user_data_folder_with_game_1(
    fs: FakeFilesystem,
    fake_user_data_folder: Path,  # pylint: disable=redefined-outer-name
) -> Path:
    """Fixture to provide a fake user data folder with a game for testing."""

    games_file = fake_user_data_folder / "games.json"  # type: ignore
    fs.create_file(str(games_file), contents=fake_game_data_1)  # type: ignore

    return fake_user_data_folder


@pytest.fixture
def fake_user_data_folder_with_game_2(
    fs: FakeFilesystem,
    fake_user_data_folder: Path,  # pylint: disable=redefined-outer-name
) -> Path:
    """Fixture to provide a fake user data folder with a game for testing."""

    games_file = fake_user_data_folder / "games.json"  # type: ignore
    fs.create_file(str(games_file), contents=fake_game_data_2)  # type: ignore

    return fake_user_data_folder


@pytest.fixture
def test_game() -> models.Py2048Game:
    """Fixture to create a test game instance."""
    board = models.GameBoard(
        grid=((0, 0, 2, 0), (0, 0, 0, 0), (0, 0, 2, 0), (0, 0, 0, 0))
    )
    state = models.GameState(board=board, score=0)
    return models.Py2048Game(game_id="test_game", state=state)

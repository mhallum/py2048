"""pytest configuration file for the py2048 project."""

from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from py2048.core import models

PATH_TO_TCSS_FILES: Path = Path(__file__).parent.parent.joinpath(
    "src", "py2048", "interfaces", "tui", "styles"
)


def load_fake_game_data(filename: str) -> str:
    """Load test game data from a JSON file."""

    path = Path(__file__).parent / "data" / filename
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def load_tcss_files() -> dict[str, str]:
    """Load all .tcss files from the styles directory."""
    styles_dir = PATH_TO_TCSS_FILES
    return {path.name: path.read_text() for path in styles_dir.glob("*.tcss")}


fake_game_data_1 = load_fake_game_data("test_game_1.json")
fake_game_data_2 = load_fake_game_data("test_game_2.json")

tcss_files = load_tcss_files()


@pytest.fixture
def fake_styles_folder(fs: FakeFilesystem) -> Path:
    """Fixture to provide a fake filesystem with .tcss files."""

    path = PATH_TO_TCSS_FILES

    fs.create_dir(path.as_posix())  # type: ignore

    return path


@pytest.fixture
def fake_styles_folder_populated(
    fs: FakeFilesystem,
    fake_styles_folder: Path,  # pylint: disable=redefined-outer-name
) -> Path:
    """Fixture to provide a fake filesystem with .tcss files."""

    for filename, content in tcss_files.items():
        fs.create_file(  # type: ignore
            fake_styles_folder.joinpath(filename).as_posix(), contents=content
        )

    return fake_styles_folder


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
        grid=((0, 0, 0, 2), (0, 0, 0, 0), (0, 0, 0, 2), (0, 0, 0, 0))
    )
    state = models.GameState(board=board, score=0)
    return models.Py2048Game(state=state)


@pytest.fixture
def almost_over_test_game() -> models.Py2048Game:
    """Fixture to create a test game instance that is almost over."""
    board = models.GameBoard(
        grid=((8, 4, 2, 0), (4, 2, 32, 16), (64, 128, 64, 2), (2, 32, 16, 4))
    )
    state = models.GameState(board=board, score=1716)
    return models.Py2048Game(state=state)

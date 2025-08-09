"""Integration tests for the game repositories."""

# pylint: disable=too-few-public-methods

from pathlib import Path

from py2048.adapters.repositories import JsonGameRepository, JsonRecordRepository
from py2048.core.models import Py2048Game
from py2048.core.models.record import GameRecord

FAKE_DATA_FOLDER: str = "fake_data_folder"


class TestJsonGameRepository:
    """Test suite for the JsonGameRepository."""

    @staticmethod
    def test_can_add_game(fake_user_data_folder_with_game_1: Path):
        """Test adding and retrieving a game from the JSON repository."""
        game = Py2048Game.create_new_game(slot_id="test_slot_1")
        repository = JsonGameRepository(folder=fake_user_data_folder_with_game_1)
        repository.add(game)

        retrieved_game = repository.get("test_slot_1")
        assert retrieved_game == game

    # This used to raise an error, but now it should not
    # because I want to leave the handling of missing games to the caller.
    @staticmethod
    def test_get_non_existent_game_returns_none(
        fake_user_data_folder_with_game_1: Path,
    ):
        """Test that trying to get a non-existent game returns None."""
        repository = JsonGameRepository(folder=fake_user_data_folder_with_game_1)
        result = repository.get("non_existent")
        assert result is None

    @staticmethod
    def test_can_get_existing_game(fake_user_data_folder_with_game_1: Path):
        """Test retrieving an existing game from the JSON repository."""
        repository = JsonGameRepository(folder=fake_user_data_folder_with_game_1)
        slot_id = "current_game"
        game = repository.get(slot_id)
        assert isinstance(game, Py2048Game)
        assert game.slot_id == slot_id
        assert game.state.board.grid == (
            (0, 0, 0, 0),
            (0, 0, 2, 0),
            (0, 0, 0, 4),
            (0, 0, 4, 2),
        )
        expected_score = 8
        assert game.state.score == expected_score
        expected_num_moves = 4
        assert len(game.moves) == expected_num_moves

    @staticmethod
    def test_missing_file_does_not_raise_error(fake_user_data_folder: Path):
        """Test that missing JSON file does not raise an error on initialization.

        Instead it initializes an empty repository.
        """
        repository = JsonGameRepository(folder=fake_user_data_folder)
        assert isinstance(repository, JsonGameRepository)
        assert len(repository.list()) == 0


class TestJsonRecordRepository:
    """Test suite for the JsonRecordRepository."""

    @staticmethod
    def assert_empty_repo(repository: JsonRecordRepository):
        """Assert that the repository is empty."""
        assert isinstance(repository, JsonRecordRepository)
        num_records = len(repository._records)  # pyright: ignore[reportPrivateUsage, protected-access] pylint: disable=protected-access
        assert num_records == 0, (
            f"Repository should be empty but has {num_records} records."
        )

    @staticmethod
    def assert_num_records(repository: JsonRecordRepository, expected_count: int):
        """Assert that the repository has the expected number of records."""
        num_records = len(repository._records)  # pyright: ignore[reportPrivateUsage, protected-access] pylint: disable=protected-access
        assert num_records == expected_count, (
            f"Repository should have {expected_count} records but has {num_records}."
        )

    @staticmethod
    def test_can_retrieve_record(
        fake_user_data_folder_with_records_file: Path,
    ):
        """Test retrieving an existing record from the JSON repository."""

        repository = JsonRecordRepository(
            folder=fake_user_data_folder_with_records_file
        )

        record = repository.get("test_uuid_1")

        expected_record = GameRecord(
            game_uuid="test_uuid_1", final_score=100, max_tile=32, number_of_moves=10
        )
        assert isinstance(record, GameRecord)
        assert record == expected_record

    @staticmethod
    def test_get_non_existent_record_returns_none(
        fake_user_data_folder_with_records_file: Path,
    ):
        """Test that trying to get a non-existent record returns None."""
        repository = JsonRecordRepository(
            folder=fake_user_data_folder_with_records_file
        )
        result = repository.get("non_existent_uuid")
        assert result is None

    def test_repo_initializes_empty_with_missing_file(
        self,
        fake_user_data_folder: Path,
    ):
        """Test that initializing with a non-existent file creates an empty repository."""
        repo = JsonRecordRepository(folder=fake_user_data_folder)

        self.assert_empty_repo(repo)

    def test_repo_initializes_empty_with_empty_file(
        self,
        fake_user_data_folder_with_empty_record_file: Path,
    ):
        """Test that initializing with an empty file creates an empty repository."""
        repo = JsonRecordRepository(folder=fake_user_data_folder_with_empty_record_file)

        self.assert_empty_repo(repo)

    def test_can_add_new_record(self, fake_user_data_folder_with_records_file: Path):
        """Test adding a new record to the JSON repository."""
        repository = JsonRecordRepository(
            folder=fake_user_data_folder_with_records_file
        )
        # Make sure the repository starts with 2 existing records
        self.assert_num_records(repository, 2)

        new_record = GameRecord(
            game_uuid="new_uuid", final_score=200, max_tile=64, number_of_moves=20
        )
        repository.add(new_record)

        assert repository.get("new_uuid") == new_record
        self.assert_num_records(repository, 3)  # Now should have 3 records

    def test_adding_with_existing_game_uuid_does_not_change_repo(
        self,
        fake_user_data_folder_with_empty_record_file: Path,
    ):
        """Test that adding an existing record does not change the repository."""

        # Start with an empty repository
        repo = JsonRecordRepository(folder=fake_user_data_folder_with_empty_record_file)
        self.assert_empty_repo(repo)

        # Add a new record
        new_record = GameRecord(
            game_uuid="new_uuid", final_score=100, max_tile=32, number_of_moves=10
        )
        repo.add(new_record)
        self.assert_num_records(repo, 1)
        assert repo.get("new_uuid") == new_record

        # Try adding the same record again
        repo.add(new_record)
        # Repository should still have only 1 record
        self.assert_num_records(repo, 1)
        # The record should still be the same
        assert repo.get("new_uuid") == new_record

        # Try adding a different record with the same UUID
        another_record = GameRecord(
            game_uuid="new_uuid", final_score=200, max_tile=64, number_of_moves=20
        )
        repo.add(another_record)
        # Repository should still have only 1 record
        self.assert_num_records(repo, 1)
        # The record should still be the first one added
        assert repo.get("new_uuid") == new_record

    def test_can_save_updated_repository(
        self,
        fake_user_data_folder_with_empty_record_file: Path,
    ):
        """Test that saving the repository updates the JSON file."""
        # Start with an empty repository
        repo = JsonRecordRepository(folder=fake_user_data_folder_with_empty_record_file)
        self.assert_empty_repo(repo)

        # Add a new record
        new_record = GameRecord(
            game_uuid="new_uuid", final_score=100, max_tile=32, number_of_moves=10
        )
        repo.add(new_record)

        # Save the repository
        repo.save()

        # Reload the repository to check if the record was saved
        reloaded_repo = JsonRecordRepository(
            folder=fake_user_data_folder_with_empty_record_file
        )
        self.assert_num_records(reloaded_repo, 1)
        assert reloaded_repo.get("new_uuid") == new_record

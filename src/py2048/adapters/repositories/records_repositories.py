"""Projection-store repositories for GameRecord objects."""

import abc
import json
from pathlib import Path
from typing import cast

from py2048.adapters.schemas import RecordSchema
from py2048.core.models.record import GameRecord


class AbstractRecordsRepository(abc.ABC):
    """Abstract base class for game record repositories."""

    @abc.abstractmethod
    def add(self, record: GameRecord) -> None:
        """Insert a record if not already present (idempotent by game_uuid)."""

    @abc.abstractmethod
    def get(self, game_uuid: str) -> "GameRecord | None":
        """Return the record for game_uuid, or None."""

    @abc.abstractmethod
    def save(self) -> None:
        """Save the current state of the repository (if applicable)."""


# Probably ok for up to about 40,000 records.
class JsonRecordRepository(AbstractRecordsRepository):
    """JSON-based implementation of the records repository."""

    def __init__(self, folder: str | Path):
        self._file_path: Path = Path(folder) / "records.json"
        self._records: dict[str, GameRecord] = {}
        self._load()

    def add(self, record: GameRecord) -> None:
        # Idempotent insert
        if record.game_uuid in self._records:
            return  # Record already exists, do nothing
        self._records[record.game_uuid] = record

    def get(self, game_uuid: str) -> GameRecord | None:
        """Retrieve a game record by its UUID."""
        return self._records.get(game_uuid)

    def _load(self) -> None:
        """Load records from the JSON file into the repository."""
        if not self._file_path.exists():
            return

        with self._file_path.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)

        if not raw_data:
            return  # Empty file, nothing to load

        records = cast(list[GameRecord], RecordSchema().load(raw_data, many=True))

        self._records.update({record.game_uuid: record for record in records})

    def save(self) -> None:
        """Save the current state of the repository to the JSON file."""

        with self._file_path.open("w", encoding="utf-8") as file:
            json.dump(RecordSchema().dump(self._records.values(), many=True), file)

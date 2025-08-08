"""Handlers for commands and events in the Py2048 game."""

import logging
from collections.abc import Callable
from random import Random

from py2048.core import commands, events
from py2048.core.models import MoveDirection, Py2048Game
from py2048.service_layer.unit_of_work import AbstractUnitOfWork

logger = logging.getLogger(__name__)


def start_new_game(
    cmd: commands.StartNewGame, uow: AbstractUnitOfWork, rng: Random = Random()
) -> None:
    """Handler for starting a new game."""
    with uow:
        new_game = Py2048Game.create_new_game(cmd.slot_id, rng=rng)
        if uow.games.get(cmd.slot_id) is not None:
            uow.games.delete(cmd.slot_id)
        uow.games.add(new_game)
        uow.commit()


def log_new_game_event(event: events.NewGameStarted) -> None:
    """Handler for logging the new game started event."""
    logger.info(
        "New game (uuid: %s) started in slot %s", event.game_uuid, event.slot_id
    )


def make_move(
    cmd: commands.MakeMove, uow: AbstractUnitOfWork, rng: Random = Random()
) -> None:
    """Handler for making a move in the game."""
    with uow:
        if not (game := uow.games.get_by_uuid(cmd.game_uuid)):
            raise ValueError(f"Game with UUID {cmd.game_uuid} not found.")
        direction = MoveDirection(cmd.direction)
        game.move(direction, rng=rng)
        uow.commit()


EVENT_HANDLERS: dict[type[events.Event], list[Callable[..., None]]] = {
    events.NewGameStarted: [log_new_game_event],
}

COMMAND_HANDLERS: dict[type[commands.Command], Callable[..., None]] = {
    commands.StartNewGame: start_new_game,
    commands.MakeMove: make_move,
}

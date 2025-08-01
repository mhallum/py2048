"""Handlers for commands and events in the Py2048 game."""

import logging
from collections.abc import Callable

from py2048.core import commands, events
from py2048.core.models import MoveDirection, Py2048Game
from py2048.service_layer.unit_of_work import AbstractUnitOfWork

logger = logging.getLogger(__name__)


def start_new_game(cmd: commands.StartNewGame, uow: AbstractUnitOfWork) -> None:
    """Handler for starting a new game."""
    new_game = Py2048Game.create_new_game(cmd.game_id)
    uow.games.add(new_game)


def log_new_game_event(event: events.NewGameStarted) -> None:
    """Handler for logging the new game started event."""
    logger.info("New game started: %s", event.game_id)


def make_move(cmd: commands.MakeMove, uow: AbstractUnitOfWork) -> None:
    """Handler for making a move in the game."""
    game = uow.games.get(cmd.game_id)
    direction = MoveDirection(cmd.direction)
    game.move(direction)


EVENT_HANDLERS: dict[type[events.Event], list[Callable[..., None]]] = {
    events.NewGameStarted: [log_new_game_event],
}

COMMAND_HANDLERS: dict[type[commands.Command], Callable[..., None]] = {
    commands.StartNewGame: start_new_game,
    commands.MakeMove: make_move,
}

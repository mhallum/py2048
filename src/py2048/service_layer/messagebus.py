"""Message bus for handling commands and events in the py2048 game."""

# pylint: disable=too-few-public-methods

import logging
from collections.abc import Callable

from py2048.core import commands, events
from py2048.service_layer.unit_of_work import AbstractUnitOfWork

logger = logging.getLogger(__name__)

Message = commands.Command | events.Event

UNKNOWN_MESSAGE_TYPE_DESCRIPTION = "Unexpected message type: {type_name}"
MISSING_HANDLER_DESCRIPTION = "No handler registered for {kind}: {message}"
UNEXPECTED_ERROR_DESCRIPTION = "An error occurred while handling {kind}: {message}"
UNEXPECTED_ERROR_WHILE_COLLECTING_EVENTS_DESCRIPTION = (
    "An error occurred while collecting events after handling {kind}: {message}"
)
HANDLING_EVENT_DESCRIPTION = "Handling event: {event} with handler: {handler}"
HANDLING_COMMAND_DESCRIPTION = "Handling command: {command}"


class MessageBus:
    """Message bus for handling commands and events in the py2048 game.

    This class is responsible for dispatching commands and events to their
    respective handlers. It acts as a central point for communication between
    different components of the game.
    """

    def __init__(
        self,
        uow: AbstractUnitOfWork,
        event_handlers: dict[type[events.Event], list[Callable[..., None]]],
        command_handlers: dict[type[commands.Command], Callable[..., None]],
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers
        self.queue: list[Message] = []

    def handle(self, message: Message):
        """Dispatch a message to the appropriate handler.

        Handles chained events and commands by maintaining a processing queue.

        Args:
            message (Message): The command or event to be handled.
        """
        self.queue = [message]
        while self.queue:  # pylint: disable=while-used
            message = self.queue.pop(0)

            match message:
                case commands.Command():
                    self._handle_command(message)
                case events.Event():
                    self._handle_event(message)
                case _:
                    raise TypeError(
                        UNKNOWN_MESSAGE_TYPE_DESCRIPTION.format(
                            type_name=type(message).__name__
                        )
                    )

    def _handle_command(self, command: commands.Command):
        """Dispatch a command to its registered handler."""
        description = HANDLING_COMMAND_DESCRIPTION.format(command=command)
        logger.debug(description)

        try:
            handler = self.command_handlers[type(command)]
        except KeyError as e:
            error_message = MISSING_HANDLER_DESCRIPTION.format(
                kind="command", message=command
            )
            logger.error(error_message)
            raise ValueError(error_message) from e

        try:
            handler(command)
        except Exception:
            error_message = UNEXPECTED_ERROR_DESCRIPTION.format(
                kind="command", message=command
            )
            logger.exception(error_message)
            raise

        try:
            self.queue.extend(self.uow.collect_new_events())
        except Exception:
            error_message = UNEXPECTED_ERROR_WHILE_COLLECTING_EVENTS_DESCRIPTION.format(
                kind="command", message=command
            )
            logger.exception(error_message)
            raise

    def _handle_event(self, event: events.Event):
        """Handle an event by dispatching it to all registered handlers."""

        if not (handlers := self.event_handlers.get(type(event), [])):
            detail = MISSING_HANDLER_DESCRIPTION.format(kind="event", message=event)
            logger.debug(detail)

        for handler in handlers:
            description = HANDLING_EVENT_DESCRIPTION.format(
                event=event,
                handler=getattr(
                    getattr(handler, "func", handler), "__name__", repr(handler)
                ),
            )
            logger.debug(description)

            try:
                handler(event)
            except Exception:  # pylint: disable=broad-except
                error_message = UNEXPECTED_ERROR_DESCRIPTION.format(
                    kind="event", message=event
                )
                logger.exception(error_message)
                continue

            try:
                self.queue.extend(self.uow.collect_new_events())
            except Exception:  # pylint: disable=broad-except
                error_message = (
                    UNEXPECTED_ERROR_WHILE_COLLECTING_EVENTS_DESCRIPTION.format(
                        kind="event", message=event
                    )
                )
                logger.exception(error_message)
                continue

"""This module bootstraps the MessageBus for the application, wiring up
commands and events with their respective handlers.
It injects dependencies into handlers, allowing for a clean separation of concerns
and easier testing."""

import inspect
from collections.abc import Callable
from functools import partial
from typing import Any

from py2048.service_layer import handlers, messagebus, unit_of_work


def bootstrap(
    uow: unit_of_work.AbstractUnitOfWork | None = None,
    event_handlers: dict[type[handlers.events.Event], list[Callable[..., None]]]
    | None = None,
    command_handlers: dict[type[handlers.commands.Command], Callable[..., None]]
    | None = None,
) -> messagebus.MessageBus:
    """Create and configure a MessageBus with injected dependencies.

    This function builds the event and command handler maps by injecting
    necessary dependencies like the Unit of Work into each handler function.

    Args:
        uow (AbstractUnitOfWork, optional): The unit of work to use.
            Defaults to an in-memory implementation.
        event_handlers (dict[type[handlers.events.Event], list[Callable[..., None]]], optional):
            A mapping of event types to lists of event handler functions.
            If None, uses default handlers.
        command_handlers (dict[type[handlers.commands.Command], Callable[..., None]], optional):
            A mapping of command types to command handler functions. If None, uses default handlers.

    Returns:
        MessageBus: A fully wired MessageBus instance.
    """
    uow = uow or unit_of_work.InMemoryUnitOfWork()
    if event_handlers is None:
        event_handlers = handlers.EVENT_HANDLERS
    if command_handlers is None:
        command_handlers = handlers.COMMAND_HANDLERS

    dependencies = {"uow": uow}

    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies) for handler in raw_handlers
        ]
        for event_type, raw_handlers in event_handlers.items()
    }

    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in command_handlers.items()
    }

    return messagebus.MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )


def inject_dependencies(
    handler: Callable[..., None], dependencies: dict[str, Any]
) -> Callable[..., None]:
    """Wrap a handler with injected dependencies.

    Inspects the handler's signature and binds only the required dependencies
    using functools.partial, allowing the handler to be called with a single message argument.

    Args:
        handler (Callable[..., None]): The original command or event handler.
        dependencies (dict[str, Any]): A mapping of dependency names to instances.

    Returns:
        Callable[..., None]: A new handler with dependencies partially applied.
    """
    params = inspect.signature(handler).parameters
    deps = {name: dependencies[name] for name in params if name in dependencies}
    return partial(handler, **deps)

"""Schemas for serializing and deserializing game data."""

from typing import Any

from marshmallow import Schema, fields, post_load

from py2048.core import models

# pylint: disable=unused-argument, no-self-use


class GameBoardSchema(Schema):
    """Schema for serializing and deserializing game board."""

    grid = fields.Tuple(
        (
            fields.Tuple((fields.Int(), fields.Int(), fields.Int(), fields.Int())),
            fields.Tuple((fields.Int(), fields.Int(), fields.Int(), fields.Int())),
            fields.Tuple((fields.Int(), fields.Int(), fields.Int(), fields.Int())),
            fields.Tuple((fields.Int(), fields.Int(), fields.Int(), fields.Int())),
        ),
        required=True,
    )

    @post_load
    def make_board(self, data: dict[str, Any], **kwargs: Any) -> models.GameBoard:
        """Create a Board instance from the deserialized data."""
        return models.GameBoard(**data)


class StateSchema(Schema):
    """Schema for serializing and deserializing game state."""

    board = fields.Nested(GameBoardSchema, required=True)
    score = fields.Int(required=True)

    @post_load
    def make_state(self, data: dict[str, Any], **kwargs: Any) -> models.GameState:
        """Create a State instance from the deserialized data."""
        return models.GameState(**data)


class MoveSchema(Schema):
    """Schema for serializing and deserializing game moves."""

    direction = fields.Enum(models.MoveDirection, required=True)
    before_state = fields.Nested(StateSchema, required=True)
    after_state = fields.Nested(StateSchema, required=True)

    @post_load
    def make_move(self, data: dict[str, Any], **kwargs: Any) -> models.Move:
        """Create a Move instance from the deserialized data."""
        return models.Move(**data)


class GameSchema(Schema):
    """Schema for serializing and deserializing game data."""

    game_id = fields.Str(required=True)
    state = fields.Nested(StateSchema, required=True)
    moves = fields.List(fields.Nested(MoveSchema))  # type: ignore

    @post_load
    def make_game(self, data: dict[str, Any], **kwargs: Any) -> models.Py2048Game:
        """Create a Game instance from the deserialized data."""
        return models.Py2048Game(**data)

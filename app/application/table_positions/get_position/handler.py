"""Table-position lookup use case."""

from __future__ import annotations

from application.errors import TablePositionNotFound
from persistence.database.models import PlayerTablePositionModel
from persistence.repositories import SQLAlchemyTablePositionRepository

from .query import GetPositionQuery


class GetPositionHandler:
    """Load a durable position without game-state calculations."""

    def __init__(self, positions: SQLAlchemyTablePositionRepository) -> None:
        """Store request-scoped collaborators."""
        self._positions = positions

    async def execute(self, query: GetPositionQuery) -> PlayerTablePositionModel:
        """Return the position or report not found."""
        position = await self._positions.get_by_id(query.position_id)
        if position is None:
            raise TablePositionNotFound()
        return position

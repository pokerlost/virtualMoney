"""Hold lookup use case."""

from __future__ import annotations

from application.errors import HoldNotFound
from persistence.database.models import HoldModel
from persistence.repositories import SQLAlchemyHoldRepository

from .query import GetHoldQuery


class GetHoldHandler:
    """Load a hold without calculating balance projections."""

    def __init__(self, holds: SQLAlchemyHoldRepository) -> None:
        """Store request-scoped collaborators."""
        self._holds = holds

    async def execute(self, query: GetHoldQuery) -> HoldModel:
        """Return the hold or report not found."""
        hold = await self._holds.get_by_id(query.hold_id)
        if hold is None:
            raise HoldNotFound()
        return hold

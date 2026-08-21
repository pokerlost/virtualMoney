"""Table-position financial operation history query."""

from __future__ import annotations

from application.errors import TablePositionNotFound
from application.pagination import (
    PaginationCursor,
    PaginationCursorCodec,
    PaginationPage,
    PaginationPolicy,
)
from persistence.projections import TablePositionOperationProjection
from persistence.queries import SQLAlchemyTablePositionOperationsQuery
from persistence.repositories import SQLAlchemyTablePositionRepository

from .query import GetOperationsQuery


class GetOperationsHandler:
    """Load bounded descending BuyIn, ReBuy, and CashOut audits."""

    def __init__(
        self,
        positions: SQLAlchemyTablePositionRepository,
        history: SQLAlchemyTablePositionOperationsQuery,
        pagination_policy: PaginationPolicy,
        cursor_codec: PaginationCursorCodec,
    ) -> None:
        """Store request-scoped collaborators."""
        self._positions = positions
        self._history = history
        self._pagination_policy = pagination_policy
        self._cursor_codec = cursor_codec

    async def execute(
        self,
        query: GetOperationsQuery,
    ) -> PaginationPage[TablePositionOperationProjection]:
        """Return one keyset page for an existing position."""
        if await self._positions.get_by_id(query.position_id) is None:
            raise TablePositionNotFound()

        limit = self._pagination_policy.resolve_limit(query.pagination)
        cursor = self._cursor_codec.decode(query.pagination.cursor)
        rows = await self._history.list_for_position(
            query.position_id,
            cursor.occurred_at if cursor is not None else None,
            cursor.item_id if cursor is not None else None,
            limit + 1,
        )
        items = rows[:limit]
        next_cursor = None
        if len(rows) > limit and items:
            last = items[-1]
            next_cursor = self._cursor_codec.encode(
                PaginationCursor(
                    occurred_at=last.created_at,
                    item_id=last.operation_id,
                ),
            )
        return PaginationPage[TablePositionOperationProjection](
            items=items,
            next_cursor=next_cursor,
        )

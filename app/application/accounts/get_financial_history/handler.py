"""Account financial history query."""

from __future__ import annotations

from application.errors import AccountNotFound
from application.pagination import (
    PaginationCursor,
    PaginationCursorCodec,
    PaginationPage,
    PaginationPolicy,
)
from persistence.projections import AccountHistoryProjection
from persistence.queries import SQLAlchemyAccountHistoryQuery
from persistence.repositories import SQLAlchemyAccountRepository

from .query import GetFinancialHistoryQuery


class GetFinancialHistoryHandler:
    """Load bounded descending immutable ledger history for an account."""

    def __init__(
        self,
        accounts: SQLAlchemyAccountRepository,
        history: SQLAlchemyAccountHistoryQuery,
        pagination_policy: PaginationPolicy,
        cursor_codec: PaginationCursorCodec,
    ) -> None:
        """Store request-scoped collaborators."""
        self._accounts = accounts
        self._history = history
        self._pagination_policy = pagination_policy
        self._cursor_codec = cursor_codec

    async def execute(
        self,
        query: GetFinancialHistoryQuery,
    ) -> PaginationPage[AccountHistoryProjection]:
        """Return one keyset page for an existing account."""
        if await self._accounts.get_by_id(query.account_id) is None:
            raise AccountNotFound()

        limit = self._pagination_policy.resolve_limit(query.pagination)
        cursor = self._cursor_codec.decode(query.pagination.cursor)
        rows = await self._history.list_for_account(
            query.account_id,
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
                    occurred_at=last.posted_at,
                    item_id=last.ledger_transaction_id,
                ),
            )
        return PaginationPage[AccountHistoryProjection](
            items=items,
            next_cursor=next_cursor,
        )

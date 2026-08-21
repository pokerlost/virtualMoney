"""Shared SQL expression for descending keyset traversal."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.sql.elements import ColumnElement, SQLColumnExpression


def descending_keyset_condition(
    occurred_at_column: SQLColumnExpression[datetime],
    item_id_column: SQLColumnExpression[UUID],
    *,
    cursor_occurred_at: datetime,
    cursor_item_id: UUID,
) -> ColumnElement[bool]:
    """Build the timestamp-and-UUID predicate for a descending keyset."""
    return or_(
        occurred_at_column < cursor_occurred_at,
        and_(
            occurred_at_column == cursor_occurred_at,
            item_id_column < cursor_item_id,
        ),
    )

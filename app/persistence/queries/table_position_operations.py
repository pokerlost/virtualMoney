"""SQLAlchemy table-position operation history query adapter."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from persistence.database.models import TableMoneyOperationModel
from persistence.projections import TablePositionOperationProjection
from persistence.repositories.base import SQLAlchemyRepository

from .keyset import descending_keyset_condition


class SQLAlchemyTablePositionOperationsQuery(SQLAlchemyRepository):
    """Read bounded immutable table-money operation projections."""

    async def list_for_position(
        self,
        position_id: UUID,
        cursor_occurred_at: datetime | None,
        cursor_item_id: UUID | None,
        limit: int,
    ) -> list[TablePositionOperationProjection]:
        """Return one descending keyset page plus any requested lookahead row."""
        statement = (
            select(
                TableMoneyOperationModel.operation_id.label("operation_id"),
                TableMoneyOperationModel.operation_type.label("operation_type"),
                TableMoneyOperationModel.amount_minor.label("amount_minor"),
                TableMoneyOperationModel.hold_id.label("hold_id"),
                TableMoneyOperationModel.ledger_transaction_id.label(
                    "ledger_transaction_id",
                ),
                TableMoneyOperationModel.created_at.label("created_at"),
            )
            .where(TableMoneyOperationModel.position_id == position_id)
            .order_by(
                TableMoneyOperationModel.created_at.desc(),
                TableMoneyOperationModel.operation_id.desc(),
            )
            .limit(limit)
        )
        if cursor_occurred_at is not None and cursor_item_id is not None:
            statement = statement.where(
                descending_keyset_condition(
                    TableMoneyOperationModel.created_at,
                    TableMoneyOperationModel.operation_id,
                    cursor_occurred_at=cursor_occurred_at,
                    cursor_item_id=cursor_item_id,
                ),
            )

        reader = await self._read_projection(statement, TablePositionOperationProjection)
        return reader.all()

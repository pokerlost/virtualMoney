"""SQLAlchemy immutable table-money operation repository adapter."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from domain.enums import TableMoneyOperationType
from persistence.database.models import TableMoneyOperationModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemyTableMoneyOperationRepository(
    SQLAlchemyEntityRepository[TableMoneyOperationModel],
):
    """Append table-money audits without committing."""

    model = TableMoneyOperationModel

    async def get_by_operation_id(
        self,
        operation_id: UUID,
    ) -> TableMoneyOperationModel | None:
        """Return one immutable table-money audit by idempotency key."""
        result = await self._read_scalar(
            select(TableMoneyOperationModel).where(
                TableMoneyOperationModel.operation_id == operation_id,
            ),
        )
        return result.one_or_none()

    async def insert_if_absent(
        self,
        *,
        operation_id: UUID,
        position_id: UUID,
        operation_type: TableMoneyOperationType,
        payload_fingerprint: str,
        hold_id: UUID | None,
        ledger_transaction_id: UUID | None,
        amount_minor: int,
    ) -> bool:
        """Append a table-money audit unless its identity already exists."""
        result = await self._read_scalar(
            insert(TableMoneyOperationModel)
            .values(
                operation_id=operation_id,
                position_id=position_id,
                operation_type=operation_type,
                payload_fingerprint=payload_fingerprint,
                hold_id=hold_id,
                ledger_transaction_id=ledger_transaction_id,
                amount_minor=amount_minor,
            )
            .on_conflict_do_nothing()
            .returning(TableMoneyOperationModel.id),
        )
        return result.one_or_none() is not None

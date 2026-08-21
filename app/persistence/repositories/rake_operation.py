"""SQLAlchemy immutable rake operation repository adapter."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from persistence.database.models import RakeOperationModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemyRakeOperationRepository(SQLAlchemyEntityRepository[RakeOperationModel]):
    """Append rake audits without owning transaction completion."""

    model = RakeOperationModel

    async def get_by_operation_id(self, operation_id: UUID) -> RakeOperationModel | None:
        """Return one immutable rake audit by idempotency key."""
        result = await self._read_scalar(
            select(RakeOperationModel).where(
                RakeOperationModel.operation_id == operation_id,
            ),
        )
        return result.one_or_none()

    async def insert_if_absent(
        self,
        *,
        operation_id: UUID,
        table_id: UUID,
        hand_id: UUID,
        asset_id: UUID,
        table_escrow_account_id: UUID,
        rake_account_id: UUID,
        amount_minor: int,
        ledger_transaction_id: UUID,
        payload_fingerprint: str,
    ) -> bool:
        """Append a rake audit unless its unique identity already exists."""
        result = await self._read_scalar(
            insert(RakeOperationModel)
            .values(
                operation_id=operation_id,
                table_id=table_id,
                hand_id=hand_id,
                asset_id=asset_id,
                table_escrow_account_id=table_escrow_account_id,
                rake_account_id=rake_account_id,
                amount_minor=amount_minor,
                ledger_transaction_id=ledger_transaction_id,
                payload_fingerprint=payload_fingerprint,
            )
            .on_conflict_do_nothing()
            .returning(RakeOperationModel.id),
        )
        return result.one_or_none() is not None

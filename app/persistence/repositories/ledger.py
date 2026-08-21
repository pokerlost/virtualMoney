"""SQLAlchemy immutable ledger repository adapter."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from domain.enums import LedgerTransactionStatus
from domain.ledger import LedgerTransactionDraft
from persistence.database.models import LedgerEntryModel, LedgerTransactionModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemyLedgerRepository(SQLAlchemyEntityRepository[LedgerTransactionModel]):
    """Persist immutable transactions and entries without committing."""

    model = LedgerTransactionModel

    async def get_by_id_with_entries(
        self,
        transaction_id: UUID,
    ) -> LedgerTransactionModel | None:
        """Return one transaction with entries loaded for ledger semantics."""
        result = await self._read_scalar(
            select(LedgerTransactionModel)
            .where(LedgerTransactionModel.id == transaction_id)
            .options(selectinload(LedgerTransactionModel.entries)),
        )
        return result.one_or_none()

    async def get_by_operation_id(
        self,
        operation_id: UUID,
    ) -> LedgerTransactionModel | None:
        """Return one transaction and its entries by idempotency key."""
        result = await self._read_scalar(
            select(LedgerTransactionModel)
            .where(LedgerTransactionModel.operation_id == operation_id)
            .options(selectinload(LedgerTransactionModel.entries)),
        )
        return result.one_or_none()

    async def find_reversal(self, transaction_id: UUID) -> LedgerTransactionModel | None:
        """Return the unique full reversal of a transaction when present."""
        result = await self._read_scalar(
            select(LedgerTransactionModel)
            .where(LedgerTransactionModel.reversal_of_transaction_id == transaction_id)
            .options(selectinload(LedgerTransactionModel.entries)),
        )
        return result.one_or_none()

    async def calculate_posted_balance_from_ledger(self, account_id: UUID) -> int:
        """Sum authoritative ledger entries for account reconciliation."""
        result = await self._read_scalar(
            select(func.coalesce(func.sum(LedgerEntryModel.amount_minor), 0)).where(
                LedgerEntryModel.account_id == account_id,
            ),
        )
        return result.one()

    async def insert(
        self,
        draft: LedgerTransactionDraft,
        asset_id: UUID,
        payload_fingerprint: str,
    ) -> UUID | None:
        """Append a journal and its entries unless the operation already exists."""
        insert_result = await self._read_scalar(
            insert(LedgerTransactionModel)
            .values(
                operation_id=draft.operation_id,
                asset_id=asset_id,
                payload_fingerprint=payload_fingerprint,
                transaction_type=draft.transaction_type,
                status=LedgerTransactionStatus.POSTED,
                reference_type=draft.reference_type,
                reference_id=draft.reference_id,
                description=draft.description,
                reversal_of_transaction_id=draft.reversal_of_transaction_id,
            )
            .on_conflict_do_nothing()
            .returning(LedgerTransactionModel.id),
        )
        transaction_id = insert_result.one_or_none()
        if transaction_id is None:
            return None

        entry_result = await self._read_scalar(
            insert(LedgerEntryModel)
            .values(
                [
                    {
                        "ledger_transaction_id": transaction_id,
                        "account_id": posting.account_id,
                        "amount_minor": posting.amount_minor,
                        "sequence": sequence,
                    }
                    for sequence, posting in enumerate(draft.postings, start=1)
                ],
            )
            .returning(LedgerEntryModel.id),
        )
        entry_result.all()
        return transaction_id

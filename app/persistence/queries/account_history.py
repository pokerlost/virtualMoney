"""SQLAlchemy account-relative ledger history query adapter."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import aliased

from domain.enums import LedgerTransactionType
from persistence.database.models import LedgerEntryModel, LedgerTransactionModel
from persistence.projections import AccountHistoryProjection
from persistence.repositories.base import SQLAlchemyRepository

from .keyset import descending_keyset_condition


class SQLAlchemyAccountHistoryQuery(SQLAlchemyRepository):
    """Read bounded account-relative immutable ledger projections."""

    async def list_for_account(
        self,
        account_id: UUID,
        cursor_occurred_at: datetime | None,
        cursor_item_id: UUID | None,
        limit: int,
    ) -> list[AccountHistoryProjection]:
        """Return one descending keyset page plus any requested lookahead row."""
        amounts = (
            select(
                LedgerEntryModel.ledger_transaction_id.label("transaction_id"),
                func.sum(LedgerEntryModel.amount_minor).label("amount_minor"),
            )
            .where(LedgerEntryModel.account_id == account_id)
            .group_by(LedgerEntryModel.ledger_transaction_id)
            .subquery()
        )
        reversal = aliased(LedgerTransactionModel)
        statement = (
            select(
                LedgerTransactionModel.id.label("ledger_transaction_id"),
                LedgerTransactionModel.operation_id.label("operation_id"),
                LedgerTransactionModel.transaction_type.label("transaction_type"),
                amounts.c.amount_minor.label("amount_minor"),
                LedgerTransactionModel.reference_type.label("reference_type"),
                LedgerTransactionModel.reference_id.label("reference_id"),
                LedgerTransactionModel.posted_at.label("posted_at"),
                LedgerTransactionModel.reversal_of_transaction_id.label(
                    "reversal_of_transaction_id",
                ),
                reversal.id.label("reversed_by_transaction_id"),
                (LedgerTransactionModel.transaction_type == LedgerTransactionType.REVERSAL).label(
                    "is_reversal"
                ),
            )
            .join(amounts, amounts.c.transaction_id == LedgerTransactionModel.id)
            .outerjoin(
                reversal,
                reversal.reversal_of_transaction_id == LedgerTransactionModel.id,
            )
            .order_by(
                LedgerTransactionModel.posted_at.desc(),
                LedgerTransactionModel.id.desc(),
            )
            .limit(limit)
        )
        if cursor_occurred_at is not None and cursor_item_id is not None:
            statement = statement.where(
                descending_keyset_condition(
                    LedgerTransactionModel.posted_at,
                    LedgerTransactionModel.id,
                    cursor_occurred_at=cursor_occurred_at,
                    cursor_item_id=cursor_item_id,
                ),
            )

        reader = await self._read_projection(statement, AccountHistoryProjection)
        return reader.all()

"""SQLAlchemy source-specific financial operation query adapter."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import literal, select

from domain.enums import FinancialOperationSource
from persistence.database.models import (
    AccountModel,
    HoldModel,
    HoldOperationModel,
    LedgerTransactionModel,
    PlayerTablePositionModel,
    RakeOperationModel,
    RefundOperationModel,
    TableMoneyOperationModel,
)
from persistence.projections import (
    HoldFinancialOperationProjection,
    LedgerFinancialOperationProjection,
    RakeFinancialOperationProjection,
    RefundFinancialOperationProjection,
    TableMoneyFinancialOperationProjection,
)
from persistence.repositories.base import SQLAlchemyRepository


class SQLAlchemyFinancialOperationQuery(SQLAlchemyRepository):
    """Resolve operation IDs into native, source-discriminated projections."""

    async def get_refund(
        self,
        operation_id: UUID,
    ) -> RefundFinancialOperationProjection | None:
        """Return a refund projection joined to its original ledger asset."""
        statement = (
            select(
                literal(FinancialOperationSource.REFUND.value).label("source"),
                RefundOperationModel.operation_id.label("operation_id"),
                RefundOperationModel.target_operation_id.label("target_operation_id"),
                LedgerTransactionModel.asset_id.label("asset_id"),
                RefundOperationModel.original_ledger_transaction_id.label(
                    "original_ledger_transaction_id",
                ),
                RefundOperationModel.reversal_ledger_transaction_id.label(
                    "reversal_ledger_transaction_id",
                ),
                RefundOperationModel.reason.label("reason"),
                RefundOperationModel.created_at.label("created_at"),
            )
            .join(
                LedgerTransactionModel,
                LedgerTransactionModel.id == RefundOperationModel.original_ledger_transaction_id,
            )
            .where(RefundOperationModel.operation_id == operation_id)
        )
        reader = await self._read_projection(
            statement,
            RefundFinancialOperationProjection,
        )
        return reader.one_or_none()

    async def get_rake(
        self,
        operation_id: UUID,
    ) -> RakeFinancialOperationProjection | None:
        """Return a source-native rake operation projection."""
        statement = select(
            literal(FinancialOperationSource.RAKE.value).label("source"),
            RakeOperationModel.operation_id.label("operation_id"),
            RakeOperationModel.amount_minor.label("amount_minor"),
            RakeOperationModel.asset_id.label("asset_id"),
            RakeOperationModel.table_id.label("table_id"),
            RakeOperationModel.hand_id.label("hand_id"),
            RakeOperationModel.table_escrow_account_id.label(
                "table_escrow_account_id",
            ),
            RakeOperationModel.rake_account_id.label("rake_account_id"),
            RakeOperationModel.ledger_transaction_id.label("ledger_transaction_id"),
            RakeOperationModel.created_at.label("created_at"),
        ).where(RakeOperationModel.operation_id == operation_id)
        reader = await self._read_projection(statement, RakeFinancialOperationProjection)
        return reader.one_or_none()

    async def get_table_money(
        self,
        operation_id: UUID,
    ) -> TableMoneyFinancialOperationProjection | None:
        """Return a table-money projection with its position context."""
        statement = (
            select(
                literal(FinancialOperationSource.TABLE_MONEY.value).label("source"),
                TableMoneyOperationModel.operation_id.label("operation_id"),
                TableMoneyOperationModel.operation_type.label("operation_type"),
                TableMoneyOperationModel.amount_minor.label("amount_minor"),
                PlayerTablePositionModel.asset_id.label("asset_id"),
                PlayerTablePositionModel.user_account_id.label("account_id"),
                PlayerTablePositionModel.table_id.label("table_id"),
                PlayerTablePositionModel.id.label("position_id"),
                TableMoneyOperationModel.hold_id.label("hold_id"),
                TableMoneyOperationModel.ledger_transaction_id.label(
                    "ledger_transaction_id",
                ),
                TableMoneyOperationModel.created_at.label("created_at"),
            )
            .join(
                PlayerTablePositionModel,
                PlayerTablePositionModel.id == TableMoneyOperationModel.position_id,
            )
            .where(TableMoneyOperationModel.operation_id == operation_id)
        )
        reader = await self._read_projection(
            statement,
            TableMoneyFinancialOperationProjection,
        )
        return reader.one_or_none()

    async def get_hold(
        self,
        operation_id: UUID,
    ) -> HoldFinancialOperationProjection | None:
        """Return a hold projection with its account asset context."""
        statement = (
            select(
                literal(FinancialOperationSource.HOLD.value).label("source"),
                HoldOperationModel.operation_id.label("operation_id"),
                HoldOperationModel.operation_type.label("operation_type"),
                HoldModel.amount_minor.label("amount_minor"),
                AccountModel.asset_id.label("asset_id"),
                HoldModel.account_id.label("account_id"),
                HoldModel.id.label("hold_id"),
                HoldOperationModel.ledger_transaction_id.label(
                    "ledger_transaction_id",
                ),
                HoldOperationModel.created_at.label("created_at"),
            )
            .join(HoldModel, HoldModel.id == HoldOperationModel.hold_id)
            .join(AccountModel, AccountModel.id == HoldModel.account_id)
            .where(HoldOperationModel.operation_id == operation_id)
        )
        reader = await self._read_projection(statement, HoldFinancialOperationProjection)
        return reader.one_or_none()

    async def get_ledger(
        self,
        operation_id: UUID,
    ) -> LedgerFinancialOperationProjection | None:
        """Return a source-native ledger transaction projection."""
        statement = select(
            literal(FinancialOperationSource.LEDGER.value).label("source"),
            LedgerTransactionModel.operation_id.label("operation_id"),
            LedgerTransactionModel.transaction_type.label("operation_type"),
            LedgerTransactionModel.status.label("status"),
            LedgerTransactionModel.asset_id.label("asset_id"),
            LedgerTransactionModel.reference_type.label("reference_type"),
            LedgerTransactionModel.reference_id.label("reference_id"),
            LedgerTransactionModel.id.label("ledger_transaction_id"),
            LedgerTransactionModel.reversal_of_transaction_id.label(
                "reversal_of_transaction_id",
            ),
            LedgerTransactionModel.posted_at.label("created_at"),
        ).where(LedgerTransactionModel.operation_id == operation_id)
        reader = await self._read_projection(statement, LedgerFinancialOperationProjection)
        return reader.one_or_none()

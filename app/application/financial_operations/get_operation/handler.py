"""Normalized financial operation lookup."""

from __future__ import annotations

from application.errors import FinancialOperationNotFound, RefundDataIntegrityError
from persistence.projections import FinancialOperationProjection
from persistence.queries import SQLAlchemyFinancialOperationQuery
from persistence.repositories import SQLAlchemyRefundOperationRepository

from .query import GetOperationQuery


class GetOperationHandler:
    """Resolve an operation across immutable financial audit sources."""

    def __init__(
        self,
        operations: SQLAlchemyFinancialOperationQuery,
        refunds: SQLAlchemyRefundOperationRepository,
    ) -> None:
        """Store request-scoped collaborators."""
        self._operations = operations
        self._refunds = refunds

    async def execute(self, query: GetOperationQuery) -> FinancialOperationProjection:
        """Return the first matching source-specific operation."""
        refund = await self._operations.get_refund(query.operation_id)
        if refund is not None:
            return refund
        if await self._refunds.get_by_operation_id(query.operation_id) is not None:
            raise RefundDataIntegrityError()

        rake = await self._operations.get_rake(query.operation_id)
        if rake is not None:
            return rake
        table_money = await self._operations.get_table_money(query.operation_id)
        if table_money is not None:
            return table_money
        hold = await self._operations.get_hold(query.operation_id)
        if hold is not None:
            return hold
        ledger = await self._operations.get_ledger(query.operation_id)
        if ledger is not None:
            return ledger
        raise FinancialOperationNotFound()

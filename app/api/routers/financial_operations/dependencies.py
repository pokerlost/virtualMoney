"""Financial operation feature composition."""

from __future__ import annotations

from api.dependencies import DatabaseSession
from application.accounts import AccountBalanceProjection
from application.financial_operations import GetOperationHandler, RefundOperationHandler
from application.ledger import LedgerPosting, LedgerReversal
from persistence.queries import SQLAlchemyFinancialOperationQuery
from persistence.repositories import (
    SQLAlchemyAccountBalanceRepository,
    SQLAlchemyAccountRepository,
    SQLAlchemyHoldOperationRepository,
    SQLAlchemyLedgerRepository,
    SQLAlchemyRefundOperationRepository,
    SQLAlchemyTableMoneyOperationRepository,
)


def provide_get_financial_operation(session: DatabaseSession) -> GetOperationHandler:
    """Compose source-discriminated operation lookup."""
    return GetOperationHandler(
        operations=SQLAlchemyFinancialOperationQuery(session),
        refunds=SQLAlchemyRefundOperationRepository(session),
    )


def provide_refund_financial_operation(
    session: DatabaseSession,
) -> RefundOperationHandler:
    """Compose full compensation from repositories sharing one session."""
    ledger = SQLAlchemyLedgerRepository(session)
    posting = LedgerPosting(
        ledger=ledger,
        balance_projection=AccountBalanceProjection(
            SQLAlchemyAccountBalanceRepository(session),
        ),
    )
    reversal = LedgerReversal(
        ledger=ledger,
        accounts=SQLAlchemyAccountRepository(session),
        posting=posting,
    )
    return RefundOperationHandler(
        ledger=ledger,
        hold_operations=SQLAlchemyHoldOperationRepository(session),
        table_operations=SQLAlchemyTableMoneyOperationRepository(session),
        refund_operations=SQLAlchemyRefundOperationRepository(session),
        ledger_reversal=reversal,
    )

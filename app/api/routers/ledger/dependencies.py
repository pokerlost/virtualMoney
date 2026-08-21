"""Ledger feature composition."""

from __future__ import annotations

from api.dependencies import DatabaseSession
from application.accounts import AccountBalanceProjection
from application.ledger import (
    GetTransactionHandler,
    LedgerPosting,
    LedgerReversal,
    PostTransactionHandler,
    ReverseTransactionHandler,
)
from persistence.repositories import (
    SQLAlchemyAccountBalanceRepository,
    SQLAlchemyAccountRepository,
    SQLAlchemyAssetRepository,
    SQLAlchemyLedgerRepository,
)


def _provide_posting(session: DatabaseSession) -> LedgerPosting:
    balances = SQLAlchemyAccountBalanceRepository(session)
    return LedgerPosting(
        ledger=SQLAlchemyLedgerRepository(session),
        balance_projection=AccountBalanceProjection(balances),
    )


def provide_get_ledger_transaction(session: DatabaseSession) -> GetTransactionHandler:
    """Compose immutable ledger lookup."""
    return GetTransactionHandler(SQLAlchemyLedgerRepository(session))


def provide_post_ledger_transaction(session: DatabaseSession) -> PostTransactionHandler:
    """Compose ledger posting from repositories sharing one session."""
    return PostTransactionHandler(
        accounts=SQLAlchemyAccountRepository(session),
        assets=SQLAlchemyAssetRepository(session),
        ledger=SQLAlchemyLedgerRepository(session),
        posting=_provide_posting(session),
    )


def provide_reverse_ledger_transaction(
    session: DatabaseSession,
) -> ReverseTransactionHandler:
    """Compose full ledger reversal from repositories sharing one session."""
    reversal = LedgerReversal(
        ledger=SQLAlchemyLedgerRepository(session),
        accounts=SQLAlchemyAccountRepository(session),
        posting=_provide_posting(session),
    )
    return ReverseTransactionHandler(reversal)

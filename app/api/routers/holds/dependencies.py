"""Hold feature composition."""

from __future__ import annotations

from api.dependencies import DatabaseSession
from application.accounts import AccountBalanceProjection
from application.holds import (
    CaptureHoldHandler,
    GetHoldHandler,
    HoldCapture,
    ReleaseHoldHandler,
    ReserveHoldHandler,
)
from application.ledger import LedgerPosting
from persistence.repositories import (
    SQLAlchemyAccountBalanceRepository,
    SQLAlchemyAccountRepository,
    SQLAlchemyHoldOperationRepository,
    SQLAlchemyHoldRepository,
    SQLAlchemyLedgerRepository,
)


def _provide_balance_projection(session: DatabaseSession) -> AccountBalanceProjection:
    return AccountBalanceProjection(SQLAlchemyAccountBalanceRepository(session))


def _provide_hold_capture(session: DatabaseSession) -> HoldCapture:
    ledger = SQLAlchemyLedgerRepository(session)
    return HoldCapture(
        accounts=SQLAlchemyAccountRepository(session),
        ledger=ledger,
        holds=SQLAlchemyHoldRepository(session),
        hold_operations=SQLAlchemyHoldOperationRepository(session),
        ledger_posting=LedgerPosting(
            ledger=ledger,
            balance_projection=_provide_balance_projection(session),
        ),
    )


def provide_get_hold(session: DatabaseSession) -> GetHoldHandler:
    """Compose hold lookup."""
    return GetHoldHandler(SQLAlchemyHoldRepository(session))


def provide_reserve_hold(session: DatabaseSession) -> ReserveHoldHandler:
    """Compose full hold reservation."""
    return ReserveHoldHandler(
        accounts=SQLAlchemyAccountRepository(session),
        holds=SQLAlchemyHoldRepository(session),
        hold_operations=SQLAlchemyHoldOperationRepository(session),
        balance_projection=_provide_balance_projection(session),
    )


def provide_release_hold(session: DatabaseSession) -> ReleaseHoldHandler:
    """Compose full hold release."""
    return ReleaseHoldHandler(
        holds=SQLAlchemyHoldRepository(session),
        hold_operations=SQLAlchemyHoldOperationRepository(session),
        balance_projection=_provide_balance_projection(session),
    )


def provide_capture_hold(session: DatabaseSession) -> CaptureHoldHandler:
    """Compose full hold capture."""
    return CaptureHoldHandler(
        holds=SQLAlchemyHoldRepository(session),
        hold_operations=SQLAlchemyHoldOperationRepository(session),
        hold_capture=_provide_hold_capture(session),
    )

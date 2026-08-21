"""Table-position feature composition."""

from __future__ import annotations

from api.dependencies import ApplicationSettingsDep, DatabaseSession
from application.accounts import AccountBalanceProjection
from application.holds import HoldCapture
from application.ledger import LedgerPosting
from application.pagination import PaginationCursorCodec, PaginationPolicy
from application.table_positions import (
    BuyInHandler,
    CashOutHandler,
    GetOperationsHandler,
    GetPositionHandler,
    ReBuyHandler,
    TableEscrowProvisioner,
)
from persistence.queries import SQLAlchemyTablePositionOperationsQuery
from persistence.repositories import (
    SQLAlchemyAccountBalanceRepository,
    SQLAlchemyAccountRepository,
    SQLAlchemyAssetRepository,
    SQLAlchemyHoldOperationRepository,
    SQLAlchemyHoldRepository,
    SQLAlchemyLedgerRepository,
    SQLAlchemyTableMoneyOperationRepository,
    SQLAlchemyTablePositionRepository,
)


def _provide_balance_projection(session: DatabaseSession) -> AccountBalanceProjection:
    return AccountBalanceProjection(SQLAlchemyAccountBalanceRepository(session))


def _provide_ledger_posting(session: DatabaseSession) -> LedgerPosting:
    return LedgerPosting(
        ledger=SQLAlchemyLedgerRepository(session),
        balance_projection=_provide_balance_projection(session),
    )


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


def _provide_escrow(session: DatabaseSession) -> TableEscrowProvisioner:
    return TableEscrowProvisioner(
        accounts=SQLAlchemyAccountRepository(session),
        assets=SQLAlchemyAssetRepository(session),
        balances=SQLAlchemyAccountBalanceRepository(session),
    )


def provide_get_position(session: DatabaseSession) -> GetPositionHandler:
    """Compose durable position lookup."""
    return GetPositionHandler(SQLAlchemyTablePositionRepository(session))


def provide_buy_in(session: DatabaseSession) -> BuyInHandler:
    """Compose atomic BuyIn from repositories sharing one session."""
    return BuyInHandler(
        accounts=SQLAlchemyAccountRepository(session),
        holds=SQLAlchemyHoldRepository(session),
        positions=SQLAlchemyTablePositionRepository(session),
        operations=SQLAlchemyTableMoneyOperationRepository(session),
        hold_capture=_provide_hold_capture(session),
        escrow_provisioner=_provide_escrow(session),
    )


def provide_re_buy(session: DatabaseSession) -> ReBuyHandler:
    """Compose atomic ReBuy from repositories sharing one session."""
    return ReBuyHandler(
        accounts=SQLAlchemyAccountRepository(session),
        holds=SQLAlchemyHoldRepository(session),
        positions=SQLAlchemyTablePositionRepository(session),
        operations=SQLAlchemyTableMoneyOperationRepository(session),
        hold_capture=_provide_hold_capture(session),
    )


def provide_cash_out(session: DatabaseSession) -> CashOutHandler:
    """Compose atomic CashOut from repositories sharing one session."""
    return CashOutHandler(
        accounts=SQLAlchemyAccountRepository(session),
        ledger=SQLAlchemyLedgerRepository(session),
        positions=SQLAlchemyTablePositionRepository(session),
        operations=SQLAlchemyTableMoneyOperationRepository(session),
        balance_projection=_provide_balance_projection(session),
        ledger_posting=_provide_ledger_posting(session),
    )


def provide_get_position_operations(
    session: DatabaseSession,
    settings: ApplicationSettingsDep,
) -> GetOperationsHandler:
    """Compose keyset-paginated table-position history."""
    return GetOperationsHandler(
        positions=SQLAlchemyTablePositionRepository(session),
        history=SQLAlchemyTablePositionOperationsQuery(session),
        pagination_policy=PaginationPolicy(
            default_limit=settings.pagination.default_limit,
            maximum_limit=settings.pagination.maximum_limit,
        ),
        cursor_codec=PaginationCursorCodec(),
    )

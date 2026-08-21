"""Account feature composition."""

from __future__ import annotations

from api.dependencies import ApplicationSettingsDep, DatabaseSession
from application.accounts import (
    CreateAccountHandler,
    GetAccountBalanceHandler,
    GetAccountHandler,
    GetFinancialHistoryHandler,
)
from application.pagination import PaginationCursorCodec, PaginationPolicy
from persistence.queries import SQLAlchemyAccountHistoryQuery
from persistence.repositories import (
    SQLAlchemyAccountBalanceRepository,
    SQLAlchemyAccountRepository,
    SQLAlchemyAssetRepository,
)


def provide_create_account(session: DatabaseSession) -> CreateAccountHandler:
    """Compose account creation from repositories sharing one session."""
    return CreateAccountHandler(
        accounts=SQLAlchemyAccountRepository(session),
        assets=SQLAlchemyAssetRepository(session),
        balances=SQLAlchemyAccountBalanceRepository(session),
    )


def provide_get_account(session: DatabaseSession) -> GetAccountHandler:
    """Compose account lookup."""
    return GetAccountHandler(SQLAlchemyAccountRepository(session))


def provide_get_account_balance(session: DatabaseSession) -> GetAccountBalanceHandler:
    """Compose account balance lookup."""
    return GetAccountBalanceHandler(
        accounts=SQLAlchemyAccountRepository(session),
        balances=SQLAlchemyAccountBalanceRepository(session),
    )


def provide_get_account_history(
    session: DatabaseSession,
    settings: ApplicationSettingsDep,
) -> GetFinancialHistoryHandler:
    """Compose the keyset-paginated account history query."""
    return GetFinancialHistoryHandler(
        accounts=SQLAlchemyAccountRepository(session),
        history=SQLAlchemyAccountHistoryQuery(session),
        pagination_policy=PaginationPolicy(
            default_limit=settings.pagination.default_limit,
            maximum_limit=settings.pagination.maximum_limit,
        ),
        cursor_codec=PaginationCursorCodec(),
    )

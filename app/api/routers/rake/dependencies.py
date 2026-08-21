"""Rake feature composition."""

from __future__ import annotations

from api.dependencies import DatabaseSession
from application.accounts import AccountBalanceProjection
from application.ledger import LedgerPosting
from application.rake import ChargeRakeHandler, RakeAccountProvisioner
from persistence.repositories import (
    SQLAlchemyAccountBalanceRepository,
    SQLAlchemyAccountRepository,
    SQLAlchemyAssetRepository,
    SQLAlchemyLedgerRepository,
    SQLAlchemyRakeOperationRepository,
)


def provide_charge_rake(session: DatabaseSession) -> ChargeRakeHandler:
    """Compose atomic rake charging from repositories sharing one session."""
    accounts = SQLAlchemyAccountRepository(session)
    balances = SQLAlchemyAccountBalanceRepository(session)
    ledger = SQLAlchemyLedgerRepository(session)
    balance_projection = AccountBalanceProjection(balances)
    return ChargeRakeHandler(
        accounts=accounts,
        ledger=ledger,
        rake_operations=SQLAlchemyRakeOperationRepository(session),
        balance_projection=balance_projection,
        ledger_posting=LedgerPosting(
            ledger=ledger,
            balance_projection=balance_projection,
        ),
        provisioner=RakeAccountProvisioner(
            accounts=accounts,
            assets=SQLAlchemyAssetRepository(session),
            balances=balances,
        ),
    )

"""Atomic posted and held balance projection calculations."""

from __future__ import annotations

from uuid import UUID

from application.errors import (
    AccountBalanceIntegrityError,
    AccountBalanceMissing,
    AccountBalanceOverflow,
)
from domain.money import POSTGRES_BIGINT_MAX, fits_postgres_bigint
from persistence.database.models import AccountBalanceModel
from persistence.repositories import SQLAlchemyAccountBalanceRepository

from .balance_projection_delta import BalanceProjectionDelta


class AccountBalanceProjection:
    """Combine deltas and increment every changed projection once."""

    def __init__(self, balances: SQLAlchemyAccountBalanceRepository) -> None:
        """Store request-scoped collaborators."""
        self._balances = balances

    async def lock(self, account_ids: list[UUID]) -> dict[UUID, AccountBalanceModel]:
        """Lock required balance rows in deterministic UUID order."""
        ordered_ids = sorted(set(account_ids), key=lambda account_id: account_id.int)
        balance_rows = await self._balances.get_many_for_update(ordered_ids)
        balances = {balance.account_id: balance for balance in balance_rows}
        if set(balances) != set(ordered_ids):
            raise AccountBalanceMissing()
        return balances

    async def apply(
        self,
        deltas: list[BalanceProjectionDelta],
        *,
        locked_balances: dict[UUID, AccountBalanceModel] | None = None,
    ) -> list[UUID]:
        """Apply combined deltas without owning transaction completion."""
        posted_deltas: dict[UUID, int] = {}
        held_deltas: dict[UUID, int] = {}
        for delta in deltas:
            posted_deltas[delta.account_id] = (
                posted_deltas.get(delta.account_id, 0) + delta.posted_delta_minor
            )
            held_deltas[delta.account_id] = (
                held_deltas.get(delta.account_id, 0) + delta.held_delta_minor
            )

        ordered_ids = sorted(
            set(posted_deltas) | set(held_deltas),
            key=lambda account_id: account_id.int,
        )
        balances = locked_balances or await self.lock(ordered_ids)
        if set(balances) != set(ordered_ids):
            raise AccountBalanceMissing()

        updated_account_ids: list[UUID] = []
        for account_id in ordered_ids:
            posted_delta = posted_deltas.get(account_id, 0)
            held_delta = held_deltas.get(account_id, 0)
            if posted_delta == 0 and held_delta == 0:
                continue
            current = balances[account_id]
            posted = current.posted_balance_minor + posted_delta
            held = current.held_balance_minor + held_delta
            if not fits_postgres_bigint(posted) or not fits_postgres_bigint(held):
                raise AccountBalanceOverflow()
            if held < 0:
                raise AccountBalanceIntegrityError()
            if not fits_postgres_bigint(posted - held):
                raise AccountBalanceOverflow()
            if current.version == POSTGRES_BIGINT_MAX:
                raise AccountBalanceOverflow()
            updated = await self._balances.apply_update(
                account_id,
                posted,
                held,
            )
            if not updated:
                raise AccountBalanceIntegrityError()
            updated_account_ids.append(account_id)

        return updated_account_ids

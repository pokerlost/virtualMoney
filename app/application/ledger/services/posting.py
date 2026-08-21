"""Reusable ledger insertion and balance projection within one transaction."""

from __future__ import annotations

from uuid import UUID

from application.accounts.services import AccountBalanceProjection, BalanceProjectionDelta
from application.errors import LedgerDataIntegrityError
from domain.ledger import LedgerTransactionDraft
from persistence.database.models import AccountBalanceModel
from persistence.repositories import SQLAlchemyLedgerRepository

from .posting_result import LedgerPostingResult


class LedgerPosting:
    """Post a validated ledger draft without owning transaction completion."""

    def __init__(
        self,
        ledger: SQLAlchemyLedgerRepository,
        balance_projection: AccountBalanceProjection,
    ) -> None:
        """Store request-scoped collaborators."""
        self._ledger = ledger
        self._balance_projection = balance_projection

    async def post(
        self,
        draft: LedgerTransactionDraft,
        asset_id: UUID,
        payload_fingerprint: str,
        *,
        additional_balance_deltas: list[BalanceProjectionDelta] | None = None,
        locked_balances: dict[UUID, AccountBalanceModel] | None = None,
    ) -> LedgerPostingResult | None:
        """Insert the journal, then apply its combined projection deltas."""
        transaction_id = await self._ledger.insert(
            draft,
            asset_id,
            payload_fingerprint,
        )
        if transaction_id is None:
            return None

        transaction = await self._ledger.get_by_id_with_entries(transaction_id)
        if transaction is None:
            raise LedgerDataIntegrityError()

        deltas = [
            BalanceProjectionDelta(
                account_id=posting.account_id,
                posted_delta_minor=posting.amount_minor,
            )
            for posting in draft.postings
        ]
        if additional_balance_deltas is not None:
            deltas.extend(additional_balance_deltas)

        updated_account_ids = await self._balance_projection.apply(
            deltas,
            locked_balances=locked_balances,
        )
        return LedgerPostingResult(
            transaction=transaction,
            updated_account_ids=updated_account_ids,
        )

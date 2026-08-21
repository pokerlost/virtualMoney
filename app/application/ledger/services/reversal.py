"""Reusable full ledger reversal within a caller-owned transaction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from application.accounts.services import index_accounts_by_id
from application.errors import (
    IdempotencyConflict,
    InvalidReversal,
    LedgerAssetMismatch,
    LedgerTransactionAlreadyReversed,
    LedgerTransactionNotFound,
    LedgerWriteConflict,
)
from application.fingerprinting import fingerprint_reverse_transaction
from domain.enums import LedgerTransactionType
from domain.ledger import LedgerTransactionDraft, Posting
from persistence.database.models import LedgerTransactionModel
from persistence.repositories import SQLAlchemyAccountRepository, SQLAlchemyLedgerRepository

from .posting import LedgerPosting
from .reversal_result import LedgerReversalResult
from .validation import validate_ledger_accounts

if TYPE_CHECKING:
    from application.ledger.reverse_transaction import ReverseLedgerTransactionCommand


def _resolve_replay(
    transaction: LedgerTransactionModel,
    expected_fingerprint: str,
) -> LedgerTransactionModel:
    if transaction.payload_fingerprint != expected_fingerprint:
        raise IdempotencyConflict()
    return transaction


class LedgerReversal:
    """Create opposite postings without opening or completing a transaction."""

    def __init__(
        self,
        ledger: SQLAlchemyLedgerRepository,
        accounts: SQLAlchemyAccountRepository,
        posting: LedgerPosting,
    ) -> None:
        """Store request-scoped collaborators."""
        self._ledger = ledger
        self._accounts = accounts
        self._posting = posting

    async def reverse(
        self,
        command: ReverseLedgerTransactionCommand,
    ) -> LedgerReversalResult:
        """Post a full reversal or return its exact idempotent replay."""
        fingerprint = fingerprint_reverse_transaction(command)
        replay = await self._ledger.get_by_operation_id(command.operation_id)
        if replay is not None:
            return LedgerReversalResult(
                transaction=_resolve_replay(replay, fingerprint),
                updated_account_ids=[],
                idempotent_replay=True,
            )

        original = await self._ledger.get_by_id_with_entries(command.transaction_id)
        if original is None:
            raise LedgerTransactionNotFound()
        if original.transaction_type is LedgerTransactionType.REVERSAL:
            raise InvalidReversal()
        if await self._ledger.find_reversal(original.id) is not None:
            raise LedgerTransactionAlreadyReversed()

        postings = tuple(
            Posting(account_id=entry.account_id, amount_minor=-entry.amount_minor)
            for entry in original.entries
        )
        account_ids = {posting.account_id for posting in postings}
        account_rows = await self._accounts.get_by_ids_for_update(account_ids)
        accounts_by_id = index_accounts_by_id(account_rows)
        asset_id = validate_ledger_accounts(postings, accounts_by_id, allow_frozen=True)
        if asset_id != original.asset_id:
            raise LedgerAssetMismatch()

        posting_result = await self._posting.post(
            LedgerTransactionDraft(
                operation_id=command.operation_id,
                transaction_type=LedgerTransactionType.REVERSAL,
                postings=postings,
                reference_type=command.reference_type,
                reference_id=command.reference_id,
                description=command.description,
                reversal_of_transaction_id=command.transaction_id,
            ),
            asset_id,
            fingerprint,
        )
        if posting_result is None:
            concurrent = await self._ledger.get_by_operation_id(command.operation_id)
            if concurrent is not None:
                return LedgerReversalResult(
                    transaction=_resolve_replay(concurrent, fingerprint),
                    updated_account_ids=[],
                    idempotent_replay=True,
                )
            if await self._ledger.find_reversal(original.id) is not None:
                raise LedgerTransactionAlreadyReversed()
            raise LedgerWriteConflict()

        return LedgerReversalResult(
            transaction=posting_result.transaction,
            updated_account_ids=posting_result.updated_account_ids,
            idempotent_replay=False,
        )

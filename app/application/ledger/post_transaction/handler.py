"""Ledger posting use case."""

from __future__ import annotations

import logfire

from application.accounts.services import index_accounts_by_id
from application.errors import (
    IdempotencyConflict,
    LedgerAssetUnavailable,
    LedgerWriteConflict,
)
from application.fingerprinting import fingerprint_post_transaction
from application.ledger.services.posting import LedgerPosting
from application.ledger.services.validation import validate_ledger_accounts
from domain.enums import AssetStatus
from domain.ledger import LedgerTransactionDraft
from persistence.database.models import LedgerTransactionModel
from persistence.repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyAssetRepository,
    SQLAlchemyLedgerRepository,
)

from .command import PostLedgerTransactionCommand


def _resolve_replay(
    transaction: LedgerTransactionModel,
    expected_fingerprint: str,
) -> LedgerTransactionModel:
    if transaction.payload_fingerprint != expected_fingerprint:
        raise IdempotencyConflict()
    return transaction


class PostTransactionHandler:
    """Post one balanced immutable adjustment."""

    def __init__(
        self,
        accounts: SQLAlchemyAccountRepository,
        assets: SQLAlchemyAssetRepository,
        ledger: SQLAlchemyLedgerRepository,
        posting: LedgerPosting,
    ) -> None:
        """Store request-scoped collaborators."""
        self._accounts = accounts
        self._assets = assets
        self._ledger = ledger
        self._posting = posting

    async def execute(self, command: PostLedgerTransactionCommand) -> LedgerTransactionModel:
        """Post an adjustment or return an exact idempotent replay."""
        draft = LedgerTransactionDraft(
            operation_id=command.operation_id,
            transaction_type=command.transaction_type,
            postings=command.postings,
            reference_type=command.reference_type,
            reference_id=command.reference_id,
            description=command.description,
        )
        fingerprint = fingerprint_post_transaction(command)
        existing = await self._ledger.get_by_operation_id(command.operation_id)
        if existing is not None:
            return _resolve_replay(existing, fingerprint)

        account_ids = {posting.account_id for posting in draft.postings}
        account_rows = await self._accounts.get_by_ids_for_update(account_ids)
        accounts_by_id = index_accounts_by_id(account_rows)
        asset_id = validate_ledger_accounts(draft.postings, accounts_by_id, allow_frozen=False)
        asset = await self._assets.get_by_id_for_update(asset_id)
        if asset is None or asset.status is not AssetStatus.ACTIVE:
            raise LedgerAssetUnavailable()

        posting_result = await self._posting.post(draft, asset_id, fingerprint)
        if posting_result is None:
            concurrent = await self._ledger.get_by_operation_id(command.operation_id)
            if concurrent is None:
                raise LedgerWriteConflict()
            return _resolve_replay(concurrent, fingerprint)

        transaction = posting_result.transaction
        logfire.info(
            "Ledger transaction posted",
            ledger_transaction_id=str(transaction.id),
            operation_id=str(transaction.operation_id),
            transaction_type=transaction.transaction_type.value,
        )
        for account_id in posting_result.updated_account_ids:
            logfire.info(
                "Account balance projection updated",
                account_id=str(account_id),
                ledger_transaction_id=str(transaction.id),
                operation_id=str(transaction.operation_id),
            )
        return transaction

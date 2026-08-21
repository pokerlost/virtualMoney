"""Reusable full hold capture within one transaction."""

from __future__ import annotations

from uuid import UUID

from application.accounts.services import BalanceProjectionDelta, index_accounts_by_id
from application.errors import (
    HoldAccountUnavailable,
    HoldAlreadyCaptured,
    HoldAlreadyReleased,
    HoldAssetMismatch,
    HoldCaptureDestinationInvalid,
    HoldDataIntegrityError,
    HoldWriteConflict,
    IdempotencyConflict,
    InvalidHoldState,
)
from application.ledger import LedgerPosting
from domain.enums import (
    AccountStatus,
    AccountType,
    HoldOperationType,
    HoldStatus,
    LedgerReferenceType,
    LedgerTransactionType,
)
from domain.ledger import LedgerTransactionDraft, Posting
from persistence.database.models import HoldModel
from persistence.repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyHoldOperationRepository,
    SQLAlchemyHoldRepository,
    SQLAlchemyLedgerRepository,
)

from .capture_result import HoldCaptureResult


def _raise_terminal_state(hold: HoldModel) -> None:
    if hold.status is HoldStatus.RELEASED:
        raise HoldAlreadyReleased()
    if hold.status is HoldStatus.CAPTURED:
        raise HoldAlreadyCaptured()
    raise InvalidHoldState()


class HoldCapture:
    """Capture an ACTIVE hold without owning transaction completion."""

    def __init__(
        self,
        accounts: SQLAlchemyAccountRepository,
        ledger: SQLAlchemyLedgerRepository,
        holds: SQLAlchemyHoldRepository,
        hold_operations: SQLAlchemyHoldOperationRepository,
        ledger_posting: LedgerPosting,
    ) -> None:
        """Store request-scoped collaborators."""
        self._accounts = accounts
        self._ledger = ledger
        self._holds = holds
        self._hold_operations = hold_operations
        self._ledger_posting = ledger_posting

    async def capture(
        self,
        *,
        operation_id: UUID,
        hold: HoldModel,
        destination_account_id: UUID,
        payload_fingerprint: str,
    ) -> HoldCaptureResult:
        """Post HOLD_CAPTURE, append audit, and transition the locked hold."""
        if hold.status is not HoldStatus.ACTIVE:
            _raise_terminal_state(hold)
        if destination_account_id == hold.account_id:
            raise HoldCaptureDestinationInvalid()

        account_rows = await self._accounts.get_by_ids_for_update(
            {hold.account_id, destination_account_id},
        )
        accounts_by_id = index_accounts_by_id(account_rows)
        source = accounts_by_id.get(hold.account_id)
        destination = accounts_by_id.get(destination_account_id)
        if source is None:
            raise HoldDataIntegrityError()
        if destination is None or destination.status is AccountStatus.CLOSED:
            raise HoldCaptureDestinationInvalid()
        if source.account_type is not AccountType.USER:
            raise HoldAccountUnavailable()
        if source.status is AccountStatus.CLOSED:
            raise HoldAccountUnavailable()
        if source.asset_id != destination.asset_id:
            raise HoldAssetMismatch()

        draft = LedgerTransactionDraft(
            operation_id=operation_id,
            transaction_type=LedgerTransactionType.HOLD_CAPTURE,
            postings=(
                Posting(account_id=source.id, amount_minor=-hold.amount_minor),
                Posting(account_id=destination.id, amount_minor=hold.amount_minor),
            ),
            reference_type=LedgerReferenceType.HOLD,
            reference_id=hold.id,
            description="Full capture of reserved funds",
        )
        posting_result = await self._ledger_posting.post(
            draft,
            source.asset_id,
            payload_fingerprint,
            additional_balance_deltas=[
                BalanceProjectionDelta(
                    account_id=source.id,
                    held_delta_minor=-hold.amount_minor,
                ),
            ],
        )
        if posting_result is None:
            record = await self._ledger.get_by_operation_id(operation_id)
            if record is None:
                raise HoldWriteConflict()
            if record.payload_fingerprint != payload_fingerprint:
                raise IdempotencyConflict()
            raise HoldDataIntegrityError()

        inserted = await self._hold_operations.insert_if_absent(
            operation_id,
            hold.id,
            HoldOperationType.CAPTURE,
            payload_fingerprint,
            posting_result.transaction.id,
        )
        if not inserted:
            existing = await self._hold_operations.get_by_operation_id(operation_id)
            if existing is not None and (
                existing.operation_type is not HoldOperationType.CAPTURE
                or existing.payload_fingerprint != payload_fingerprint
            ):
                raise IdempotencyConflict()
            # Ledger and projection writes occurred before the audit conflict.
            # Raising forces the external request transaction to roll them back.
            raise HoldWriteConflict()

        captured = await self._holds.save_captured(
            hold.id,
            posting_result.transaction.id,
        )
        if captured is None:
            raise HoldWriteConflict()
        return HoldCaptureResult(
            hold=captured,
            ledger_transaction=posting_result.transaction,
            updated_account_ids=posting_result.updated_account_ids,
        )

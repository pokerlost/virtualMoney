"""Deterministic semantic payload fingerprints."""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING

from domain.enums import (
    FingerprintAction,
    HoldOperationType,
    TableMoneyOperationType,
)
from domain.types import validate_reference_pair

if TYPE_CHECKING:
    from application.financial_operations.refund_operation import RefundFinancialOperationCommand
    from application.holds.capture_hold import CaptureHoldCommand
    from application.holds.release_hold import ReleaseHoldCommand
    from application.holds.reserve_hold import ReserveHoldCommand
    from application.ledger.post_transaction import PostLedgerTransactionCommand
    from application.ledger.reverse_transaction import ReverseLedgerTransactionCommand
    from application.rake.charge_rake import ChargeRakeCommand
    from application.table_positions.buy_in import BuyInCommand
    from application.table_positions.cash_out import CashOutCommand
    from application.table_positions.re_buy import ReBuyCommand


def canonical_fingerprint(payload: dict[str, object]) -> str:
    """Return a stable SHA-256 digest of a canonical business payload."""
    canonical_payload = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical_payload).hexdigest()


def fingerprint_reserve_hold(command: ReserveHoldCommand) -> str:
    """Return a stable fingerprint of reserve semantics."""
    return canonical_fingerprint(
        {
            "account_id": str(command.account_id),
            "amount_minor": command.amount_minor,
            "operation_type": HoldOperationType.RESERVE.value,
            "reference_id": (
                str(command.reference_id) if command.reference_id is not None else None
            ),
            "reference_type": command.reference_type,
            "version": 1,
        },
    )


def fingerprint_capture_hold(command: CaptureHoldCommand) -> str:
    """Return a stable fingerprint of capture semantics."""
    return canonical_fingerprint(
        {
            "destination_account_id": str(command.destination_account_id),
            "hold_id": str(command.hold_id),
            "operation_type": HoldOperationType.CAPTURE.value,
            "version": 1,
        },
    )


def fingerprint_release_hold(command: ReleaseHoldCommand) -> str:
    """Return a stable fingerprint of release semantics."""
    return canonical_fingerprint(
        {
            "hold_id": str(command.hold_id),
            "operation_type": HoldOperationType.RELEASE.value,
            "version": 1,
        },
    )


def fingerprint_refund_operation(command: RefundFinancialOperationCommand) -> str:
    """Return the stable identity of full compensation semantics."""
    return canonical_fingerprint(
        {
            "action": FingerprintAction.REFUND_FINANCIAL_OPERATION.value,
            "reason": command.reason,
            "target_operation_id": str(command.target_operation_id),
            "version": 1,
        },
    )


def fingerprint_re_buy(command: ReBuyCommand) -> str:
    """Return the stable identity of ReBuy semantics."""
    return canonical_fingerprint(
        {
            "hold_id": str(command.hold_id),
            "operation_type": TableMoneyOperationType.REBUY.value,
            "position_id": str(command.position_id),
            "version": 1,
        },
    )


def fingerprint_post_transaction(command: PostLedgerTransactionCommand) -> str:
    """Return the stable identity of the economic payload."""
    return canonical_fingerprint(
        {
            "action": FingerprintAction.POST_LEDGER_TRANSACTION.value,
            "description": command.description,
            "postings": [
                {
                    "account_id": str(posting.account_id),
                    "amount_minor": posting.amount_minor,
                }
                for posting in command.postings
            ],
            "reference_id": (
                str(command.reference_id) if command.reference_id is not None else None
            ),
            "reference_type": command.reference_type,
            "transaction_type": command.transaction_type.value,
            "version": 1,
        },
    )


def fingerprint_cash_out(command: CashOutCommand) -> str:
    """Return the stable identity of CashOut semantics."""
    return canonical_fingerprint(
        {
            "amount_minor": command.amount_minor,
            "operation_type": TableMoneyOperationType.CASH_OUT.value,
            "position_id": str(command.position_id),
            "version": 1,
        },
    )


def fingerprint_buy_in(command: BuyInCommand) -> str:
    """Return the stable identity of BuyIn semantics."""
    return canonical_fingerprint(
        {
            "hold_id": str(command.hold_id),
            "operation_type": TableMoneyOperationType.BUY_IN.value,
            "table_id": str(command.table_id),
            "user_id": str(command.user_id),
            "version": 1,
        },
    )


def fingerprint_charge_rake(command: ChargeRakeCommand) -> str:
    """Return the stable identity of rake charge semantics."""
    return canonical_fingerprint(
        {
            "action": FingerprintAction.CHARGE_RAKE.value,
            "amount_minor": command.amount_minor,
            "asset_id": str(command.asset_id),
            "hand_id": str(command.hand_id),
            "table_id": str(command.table_id),
            "version": 1,
        },
    )


def fingerprint_reverse_transaction(command: ReverseLedgerTransactionCommand) -> str:
    """Return the stable identity of the reversal request."""
    validate_reference_pair(command.reference_type, command.reference_id)
    return canonical_fingerprint(
        {
            "action": FingerprintAction.REVERSE_LEDGER_TRANSACTION.value,
            "description": command.description,
            "reference_id": (
                str(command.reference_id) if command.reference_id is not None else None
            ),
            "reference_type": command.reference_type,
            "transaction_id": str(command.transaction_id),
            "version": 1,
        },
    )

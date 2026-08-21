"""Canonical fingerprint action discriminators."""

from __future__ import annotations

from enum import StrEnum


class FingerprintAction(StrEnum):
    """Identify operation families in versioned semantic fingerprints."""

    REFUND_FINANCIAL_OPERATION = "REFUND_FINANCIAL_OPERATION"
    POST_LEDGER_TRANSACTION = "POST_LEDGER_TRANSACTION"
    CHARGE_RAKE = "CHARGE_RAKE"
    REVERSE_LEDGER_TRANSACTION = "REVERSE_LEDGER_TRANSACTION"

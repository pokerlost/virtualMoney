"""Immutable ledger validation errors."""

from __future__ import annotations

from .base import DomainValidationError


class InvalidPosting(DomainValidationError):
    """A posting violates amount, cardinality, or sequence invariants."""

    error_code = "INVALID_LEDGER_POSTING"
    public_message = "The ledger posting contains invalid data."


class LedgerTransactionUnbalanced(DomainValidationError):
    """The signed postings do not sum to zero."""

    error_code = "LEDGER_TRANSACTION_UNBALANCED"
    public_message = "Ledger transaction postings must sum to zero."


class InvalidLedgerTransaction(DomainValidationError):
    """Immutable ledger metadata or structure is inconsistent."""

    error_code = "INVALID_LEDGER_TRANSACTION"
    public_message = "The ledger transaction has an invalid structure."

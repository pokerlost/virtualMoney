"""LedgerAssetMismatch application error."""

from __future__ import annotations

from application.errors.base import InvalidOperationError


class LedgerAssetMismatch(InvalidOperationError):
    """One journal contains accounts for different assets."""

    error_code = "LEDGER_ASSET_MISMATCH"
    public_message = "Every account in a ledger transaction must use the same asset."

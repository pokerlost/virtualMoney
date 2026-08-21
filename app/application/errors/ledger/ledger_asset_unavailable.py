"""LedgerAssetUnavailable application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class LedgerAssetUnavailable(ConflictError):
    """The asset cannot accept a new ledger operation."""

    error_code = "LEDGER_ASSET_UNAVAILABLE"
    public_message = "The internal asset is unavailable for a new ledger operation."

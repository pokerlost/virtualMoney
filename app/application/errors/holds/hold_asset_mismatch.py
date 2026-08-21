"""HoldAssetMismatch application error."""

from __future__ import annotations

from application.errors.base import InvalidOperationError


class HoldAssetMismatch(InvalidOperationError):
    """Hold source and destination use different assets."""

    error_code = "HOLD_ASSET_MISMATCH"
    public_message = "The hold source and destination accounts must use the same asset."

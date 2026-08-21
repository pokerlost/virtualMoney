"""PositionAssetMismatch application error."""

from __future__ import annotations

from application.errors.base import InvalidOperationError


class PositionAssetMismatch(InvalidOperationError):
    """A linked position resource uses another asset."""

    error_code = "POSITION_ASSET_MISMATCH"
    public_message = "The financial position and linked accounts use different assets."

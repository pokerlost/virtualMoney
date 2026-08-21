"""AssetNotFound application error."""

from __future__ import annotations

from application.errors.base import NotFoundError


class AssetNotFound(NotFoundError):
    """The requested asset does not exist."""

    error_code = "ASSET_NOT_FOUND"
    public_message = "The internal financial asset was not found."

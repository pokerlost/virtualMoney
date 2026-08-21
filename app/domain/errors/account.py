"""Account validation errors."""

from __future__ import annotations

from .base import DomainValidationError


class InvalidAccountOwnership(DomainValidationError):
    """An account purpose and owner namespace are incompatible."""

    error_code = "INVALID_ACCOUNT_OWNERSHIP"
    public_message = "The owner type is incompatible with the account purpose."

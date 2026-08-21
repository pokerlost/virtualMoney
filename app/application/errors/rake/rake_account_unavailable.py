"""RakeAccountUnavailable application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class RakeAccountUnavailable(ConflictError):
    """The RAKE account or asset cannot accept a charge."""

    error_code = "RAKE_ACCOUNT_UNAVAILABLE"
    public_message = "The system rake account is unavailable for this operation."

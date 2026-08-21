"""IdempotencyConflict application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class IdempotencyConflict(ConflictError):
    """An operation identifier is bound to another semantic payload."""

    error_code = "IDEMPOTENCY_CONFLICT"
    public_message = "The operation identifier was reused with a different payload."

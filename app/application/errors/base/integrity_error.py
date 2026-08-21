"""IntegrityError semantic application error category."""

from __future__ import annotations

from .application_error import ApplicationError


class IntegrityError(ApplicationError):
    """Persisted financial records violate an internal invariant."""

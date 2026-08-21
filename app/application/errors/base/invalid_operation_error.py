"""InvalidOperationError semantic application error category."""

from __future__ import annotations

from .application_error import ApplicationError


class InvalidOperationError(ApplicationError):
    """Semantically invalid operation input or relationship."""

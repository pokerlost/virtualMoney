"""NotFoundError semantic application error category."""

from __future__ import annotations

from .application_error import ApplicationError


class NotFoundError(ApplicationError):
    """Requested application resource does not exist."""

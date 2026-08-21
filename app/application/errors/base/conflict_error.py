"""ConflictError semantic application error category."""

from __future__ import annotations

from .application_error import ApplicationError


class ConflictError(ApplicationError):
    """Current state conflicts with the requested operation."""

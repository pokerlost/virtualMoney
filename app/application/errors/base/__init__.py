"""Transport-independent application error categories."""

from __future__ import annotations

from .application_error import ApplicationError
from .conflict_error import ConflictError
from .integrity_error import IntegrityError
from .invalid_operation_error import InvalidOperationError
from .not_found_error import NotFoundError

__all__ = (
    "ApplicationError",
    "ConflictError",
    "IntegrityError",
    "InvalidOperationError",
    "NotFoundError",
)

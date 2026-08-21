"""ApplicationError semantic application error category."""

from __future__ import annotations


class ApplicationError(Exception):
    """Base expected application failure."""

    error_code = "APPLICATION_ERROR"
    public_message = "The operation cannot be completed."

"""FinancialOperationNotFound application error."""

from __future__ import annotations

from application.errors.base import NotFoundError


class FinancialOperationNotFound(NotFoundError):
    """The target business operation does not exist."""

    error_code = "FINANCIAL_OPERATION_NOT_FOUND"
    public_message = "The financial operation was not found."

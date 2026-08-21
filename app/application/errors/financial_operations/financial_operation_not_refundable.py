"""FinancialOperationNotRefundable application error."""

from __future__ import annotations

from application.errors.base import ConflictError


class FinancialOperationNotRefundable(ConflictError):
    """The target has no safely reversible complete journal."""

    error_code = "FINANCIAL_OPERATION_NOT_REFUNDABLE"
    public_message = "The financial operation does not support full compensation."

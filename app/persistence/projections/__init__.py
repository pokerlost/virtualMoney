"""Typed immutable projections produced by persistence queries."""

from __future__ import annotations

from .account_history import AccountHistoryProjection
from .base import ProjectionModel
from .financial_operation import (
    FinancialOperationProjection,
    HoldFinancialOperationProjection,
    LedgerFinancialOperationProjection,
    RakeFinancialOperationProjection,
    RefundFinancialOperationProjection,
    TableMoneyFinancialOperationProjection,
)
from .table_position_operation import TablePositionOperationProjection

__all__ = (
    "AccountHistoryProjection",
    "FinancialOperationProjection",
    "HoldFinancialOperationProjection",
    "LedgerFinancialOperationProjection",
    "ProjectionModel",
    "RakeFinancialOperationProjection",
    "RefundFinancialOperationProjection",
    "TableMoneyFinancialOperationProjection",
    "TablePositionOperationProjection",
)

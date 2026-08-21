"""Discriminated financial operation projection union."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .hold_financial_operation import HoldFinancialOperationProjection
from .ledger_financial_operation import LedgerFinancialOperationProjection
from .rake_financial_operation import RakeFinancialOperationProjection
from .refund_financial_operation import RefundFinancialOperationProjection
from .table_money_financial_operation import TableMoneyFinancialOperationProjection

type FinancialOperationProjection = Annotated[
    LedgerFinancialOperationProjection
    | HoldFinancialOperationProjection
    | TableMoneyFinancialOperationProjection
    | RakeFinancialOperationProjection
    | RefundFinancialOperationProjection,
    Field(discriminator="source"),
]

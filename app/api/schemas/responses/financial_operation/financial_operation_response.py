"""Discriminated public financial operation response union."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .hold_financial_operation_response import HoldFinancialOperationResponse
from .ledger_financial_operation_response import LedgerFinancialOperationResponse
from .rake_financial_operation_response import RakeFinancialOperationResponse
from .refund_financial_operation_response import RefundFinancialOperationResponse
from .table_money_financial_operation_response import TableMoneyFinancialOperationResponse

type FinancialOperationResponse = Annotated[
    LedgerFinancialOperationResponse
    | HoldFinancialOperationResponse
    | TableMoneyFinancialOperationResponse
    | RakeFinancialOperationResponse
    | RefundFinancialOperationResponse,
    Field(discriminator="source"),
]

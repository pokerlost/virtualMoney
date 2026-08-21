"""Public router packages."""

from __future__ import annotations

from .accounts import router as account_router
from .assets import router as asset_router
from .financial_operations import router as financial_operation_router
from .holds import router as hold_router
from .ledger import router as ledger_router
from .rake import router as rake_router
from .root import router as root_router
from .table_positions import router as table_position_router

__all__ = (
    "account_router",
    "asset_router",
    "financial_operation_router",
    "hold_router",
    "ledger_router",
    "rake_router",
    "root_router",
    "table_position_router",
)

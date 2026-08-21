"""Deterministic registration of logical API areas."""

from __future__ import annotations

from fastapi import FastAPI

from api.routers import (
    account_router,
    asset_router,
    financial_operation_router,
    hold_router,
    ledger_router,
    rake_router,
    root_router,
    table_position_router,
)


def configure_routers(app: FastAPI) -> None:
    """Register all logical base routers."""
    app.include_router(root_router)
    app.include_router(asset_router)
    app.include_router(account_router)
    app.include_router(ledger_router)
    app.include_router(hold_router)
    app.include_router(table_position_router)
    app.include_router(rake_router)
    app.include_router(financial_operation_router)

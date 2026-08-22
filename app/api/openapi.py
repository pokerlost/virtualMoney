"""Focused OpenAPI metadata."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

API_DESCRIPTION = (
    "virtualMoney is the PostgreSQL-backed source of truth for internal poker assets, "
    "accounts, immutable double-entry ledger entries, balances, holds, table escrow, "
    "BuyIn, ReBuy, CashOut, rake, full compensation, and financial history. "
    "Current "
    "internal endpoints are unauthenticated pending a future external Auth Service contract."
)


class OpenAPITag(StrEnum):
    """Name the bounded public API areas."""

    SERVICE = "Service"
    ASSETS = "Assets"
    ACCOUNTS = "Accounts"
    LEDGER = "Ledger"
    HOLDS = "Holds"
    TABLE_POSITIONS = "Table Positions"
    RAKE = "Rake"
    FINANCIAL_OPERATIONS = "Financial Operations"


def build_openapi_tags() -> list[dict[str, str]]:
    """Build fresh metadata for one application instance."""
    return [
        {
            "name": OpenAPITag.SERVICE.value,
            "description": "Parameterless service availability endpoint.",
        },
        {
            "name": OpenAPITag.ASSETS.value,
            "description": "Metadata queries for internal financial assets.",
        },
        {
            "name": OpenAPITag.ACCOUNTS.value,
            "description": "Accounts, projections, and keyset-paginated financial history.",
        },
        {
            "name": OpenAPITag.LEDGER.value,
            "description": "Immutable double-entry posting, lookup, and full reversal.",
        },
        {
            "name": OpenAPITag.HOLDS.value,
            "description": "Full reserve, lookup, release, and capture operations.",
        },
        {
            "name": OpenAPITag.TABLE_POSITIONS.value,
            "description": "BuyIn, ReBuy, CashOut, and durable operation history.",
        },
        {
            "name": OpenAPITag.RAKE.value,
            "description": "Poker Server supplied rake transfers from table escrow.",
        },
        {
            "name": OpenAPITag.FINANCIAL_OPERATIONS.value,
            "description": "Source-discriminated operation lookup and full compensation.",
        },
    ]


def add_pokerlost_service_extension(
    openapi_schema: dict[str, Any], service_id: str
) -> dict[str, Any]:
    """Attach canonical PokerLost service metadata to the generated OpenAPI schema."""
    openapi_schema["x-pokerlost-service"] = {"id": service_id}
    return openapi_schema

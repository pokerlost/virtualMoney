"""Service observability boundary."""

from __future__ import annotations

from .logfire import (
    configure_observability,
    instrument_database,
    instrument_fastapi,
)

__all__ = (
    "configure_observability",
    "instrument_database",
    "instrument_fastapi",
)

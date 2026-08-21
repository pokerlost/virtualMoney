"""Privacy-safe Pydantic Logfire configuration and instrumentation."""

from __future__ import annotations

from typing import Literal

import logfire
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from configuration import Settings


def configure_observability(settings: Settings) -> None:
    """Configure the process-wide Logfire SDK once at composition time."""
    logfire_settings = settings.logfire
    console: logfire.ConsoleOptions | Literal[False]
    if logfire_settings.enabled and logfire_settings.console:
        console = logfire.ConsoleOptions(
            min_log_level=logfire_settings.minimum_level,
        )
    else:
        console = False

    logfire.configure(
        service_name=settings.application.service_name,
        environment=settings.application.environment.value,
        send_to_logfire=(logfire_settings.send_to_logfire if logfire_settings.enabled else False),
        console=console,
        inspect_arguments=False,
        min_level=logfire_settings.minimum_level,
        scrubbing=logfire.ScrubbingOptions(
            extra_patterns=(
                "authorization",
                "cookie",
                "credential",
                "database[._ -]?url",
                "dsn",
                "financial[._ -]?payload",
                "token",
            ),
        ),
    )


def instrument_fastapi(app: FastAPI, settings: Settings) -> None:
    """Instrument route timing without recording headers or parsed arguments."""
    if not settings.logfire.enabled:
        return

    logfire.instrument_fastapi(
        app,
        capture_headers=False,
        record_send_receive=False,
        extra_spans=False,
    )


def instrument_database(engine: AsyncEngine, settings: Settings) -> None:
    """Instrument the concrete async SQLAlchemy engine once."""
    if not settings.logfire.enabled:
        return

    logfire.instrument_sqlalchemy(engine=engine)

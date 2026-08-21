"""Central handling of SQLAlchemy infrastructure failures."""

from __future__ import annotations

import logfire
from fastapi import Request, status
from fastapi.responses import JSONResponse


async def handle_database_unavailable(
    _request: Request,
    exception: Exception,
) -> JSONResponse:
    """Return a retryable service response for connectivity or pool failures."""
    logfire.error(
        "Database operation unavailable",
        _exc_info=exception,
    )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "ok": False,
            "result": None,
            "error": "DATABASE_UNAVAILABLE",
            "errorMessage": "The database is temporarily unavailable.",
        },
    )


async def handle_database_error(
    _request: Request,
    exception: Exception,
) -> JSONResponse:
    """Hide all unclassified SQLAlchemy details from clients."""
    logfire.error(
        "Unclassified database operation failed",
        _exc_info=exception,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "ok": False,
            "result": None,
            "error": "DATABASE_ERROR",
            "errorMessage": "An internal database error occurred.",
        },
    )

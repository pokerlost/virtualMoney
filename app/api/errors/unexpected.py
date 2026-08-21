"""Unexpected exception handler."""

from __future__ import annotations

import logfire
from fastapi import Request, status
from fastapi.responses import JSONResponse


async def handle_unexpected_exception(
    _request: Request,
    exception: Exception,
) -> JSONResponse:
    """Record a safe diagnostic and hide internal details from clients."""
    logfire.error(
        "Unhandled application exception",
        _exc_info=exception,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "ok": False,
            "result": None,
            "error": "HTTP_500_INTERNAL_SERVER_ERROR",
            "errorMessage": "An internal service error occurred.",
        },
    )

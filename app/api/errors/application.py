"""Transport mapping for semantic application errors."""

from __future__ import annotations

import logfire
from fastapi import Request, status
from fastapi.responses import JSONResponse

from application.errors import (
    ApplicationError,
    ConflictError,
    InvalidOperationError,
    NotFoundError,
)


async def handle_application_error(
    _request: Request,
    exception: Exception,
) -> JSONResponse:
    """Map a transport-independent semantic category to HTTP."""
    if isinstance(exception, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exception, ConflictError):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exception, InvalidOperationError):
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    elif isinstance(exception, ApplicationError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        logfire.error("Misregistered application error handler", _exc_info=exception)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "ok": False,
                "result": None,
                "error": "INTERNAL_ERROR",
                "errorMessage": "An internal service error occurred.",
            },
        )

    logfire.info(
        "Application operation rejected",
        error_code=exception.error_code,
        http_status_code=status_code,
    )
    return JSONResponse(
        status_code=status_code,
        content={
            "ok": False,
            "result": None,
            "error": exception.error_code,
            "errorMessage": exception.public_message,
        },
    )

"""Framework exception handler."""

from __future__ import annotations

from http import HTTPStatus

from fastapi import Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from .unexpected import handle_unexpected_exception


async def handle_http_exception(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Wrap framework HTTP failures without exposing implementation detail."""
    if not isinstance(exception, HTTPException):
        return await handle_unexpected_exception(request, exception)

    try:
        status_name = HTTPStatus(exception.status_code).name
    except ValueError:
        status_name = "ERROR"
    if exception.status_code == status.HTTP_404_NOT_FOUND:
        message = "The requested HTTP endpoint was not found."
    elif exception.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        message = "The HTTP method is not allowed for this endpoint."
    else:
        message = "The service rejected the HTTP request."
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "ok": False,
            "result": None,
            "error": f"HTTP_{exception.status_code}_{status_name}",
            "errorMessage": message,
        },
        headers=exception.headers,
    )

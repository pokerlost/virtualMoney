"""Request, application-model, and domain validation handlers."""

from __future__ import annotations

import logfire
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from domain.errors import DomainValidationError


async def handle_request_validation_error(
    _request: Request,
    exception: Exception,
) -> JSONResponse:
    """Return the standard envelope for invalid HTTP input."""
    logfire.info(
        "HTTP request validation failed",
        validation_error_count=(
            len(exception.errors()) if isinstance(exception, RequestValidationError) else 0
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "ok": False,
            "result": None,
            "error": "HTTP_422_UNPROCESSABLE_CONTENT",
            "errorMessage": "The request did not pass validation.",
        },
    )


async def handle_pydantic_validation_error(
    _request: Request,
    exception: Exception,
) -> JSONResponse:
    """Return HTTP 422 for invalid application-boundary models."""
    logfire.info(
        "Application model validation failed",
        validation_error_count=(
            exception.error_count() if isinstance(exception, ValidationError) else 0
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "ok": False,
            "result": None,
            "error": "HTTP_422_UNPROCESSABLE_CONTENT",
            "errorMessage": "The operation parameters did not pass validation.",
        },
    )


async def handle_domain_validation_error(
    _request: Request,
    exception: Exception,
) -> JSONResponse:
    """Expose only the stable safe domain validation contract."""
    if isinstance(exception, DomainValidationError):
        error_code = exception.error_code
        public_message = exception.public_message
    else:
        error_code = "INVALID_DOMAIN_VALUE"
        public_message = "The submitted data violates the financial model rules."
    logfire.info("Domain validation failed", error_code=error_code)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "ok": False,
            "result": None,
            "error": error_code,
            "errorMessage": public_message,
        },
    )

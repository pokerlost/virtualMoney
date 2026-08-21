"""Exception-handler registration."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.exc import TimeoutError as SQLAlchemyTimeoutError

from application.errors import ApplicationError
from domain.errors import DomainValidationError

from .application import handle_application_error
from .database import handle_database_error, handle_database_unavailable
from .framework import handle_http_exception
from .unexpected import handle_unexpected_exception
from .validation import (
    handle_domain_validation_error,
    handle_pydantic_validation_error,
    handle_request_validation_error,
)


def configure_exception_handlers(app: FastAPI) -> None:
    """Register focused handlers in the application composition root."""
    app.add_exception_handler(ApplicationError, handle_application_error)
    app.add_exception_handler(DomainValidationError, handle_domain_validation_error)
    app.add_exception_handler(OperationalError, handle_database_unavailable)
    app.add_exception_handler(SQLAlchemyTimeoutError, handle_database_unavailable)
    app.add_exception_handler(SQLAlchemyError, handle_database_error)
    app.add_exception_handler(HTTPException, handle_http_exception)
    app.add_exception_handler(Exception, handle_unexpected_exception)
    app.add_exception_handler(RequestValidationError, handle_request_validation_error)
    app.add_exception_handler(ValidationError, handle_pydantic_validation_error)

"""Регистрация базовых FastAPI exception handlers."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from virtual_money.api.schemas.responses import ApiResponse, create_error_response

logger = logging.getLogger(__name__)


def _json_response(response: ApiResponse[None]) -> JSONResponse:
    return JSONResponse(
        status_code=response.status_code,
        content=response.model_dump(mode="json", by_alias=True),
    )


async def handle_request_validation_error(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Скрывает внутренние детали validation failure за стабильным API contract."""
    if not isinstance(exception, RequestValidationError):
        raise TypeError("validation handler received an incompatible exception")
    logger.info(
        "Request validation failed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "error_count": len(exception.errors()),
        },
    )
    response = create_error_response(
        error="HTTP_422_UNPROCESSABLE_ENTITY",
        error_message="Запрос не прошёл validation.",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
    return _json_response(response)


async def handle_unexpected_exception(request: Request, exception: Exception) -> JSONResponse:
    """Логирует unexpected exception и возвращает клиенту безопасное сообщение."""
    logger.exception(
        "Unhandled application exception",
        exc_info=exception,
        extra={"method": request.method, "path": request.url.path},
    )
    response = create_error_response(
        error="HTTP_500_INTERNAL_SERVER_ERROR",
        error_message="Произошла внутренняя ошибка сервиса.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    return _json_response(response)


def configure_exception_handlers(app: FastAPI) -> None:
    """Подключает централизованные handlers к указанному FastAPI application.

    Args:
        app: Изменяемый экземпляр FastAPI, создаваемый composition root.
    """
    app.add_exception_handler(RequestValidationError, handle_request_validation_error)
    app.add_exception_handler(Exception, handle_unexpected_exception)

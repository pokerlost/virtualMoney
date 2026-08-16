"""Единый generic envelope для обычных JSON-ответов API."""

from typing import Self

from pydantic import Field, model_validator

from virtual_money.common.models.base import AppBaseModel


class ApiResponse[T](AppBaseModel):
    """Представляет согласованный success/error contract HTTP API."""

    ok: bool = Field(description="Признак успешного выполнения запроса.")
    result: T | None = Field(description="Результат успешного запроса.")
    error: str | None = Field(
        description="Стабильный machine-readable код ошибки.",
    )
    error_message: str | None = Field(
        description="Безопасное для клиента описание ошибки.",
    )
    status_code: int = Field(
        ge=100,
        le=599,
        description="Фактический HTTP status ответа.",
    )

    @model_validator(mode="after")
    def validate_response_state(self) -> Self:
        """Не допускает противоречивого состояния response envelope."""
        if self.ok:
            if self.status_code >= 400:
                raise ValueError("successful response must use a non-error HTTP status")
            if self.error is not None or self.error_message is not None:
                raise ValueError("successful response cannot contain error information")
        else:
            if self.status_code < 400:
                raise ValueError("error response must use an error HTTP status")
            if self.result is not None:
                raise ValueError("error response cannot contain a result")
            if not self.error or not self.error_message:
                raise ValueError("error response must contain error information")
        return self


def create_success_response[T](*, result: T | None, status_code: int) -> ApiResponse[T]:
    """Создаёт непротиворечивый success response с фактическим HTTP status.

    Args:
        result: Typed payload; значение `None` допустимо для успешного ответа.
        status_code: Фактический non-error HTTP status, который вернёт transport layer.

    Returns:
        Validated generic response envelope.

    Raises:
        ValidationError: Переданный status не соответствует success response.
    """
    return ApiResponse[T](
        ok=True,
        result=result,
        error=None,
        error_message=None,
        status_code=status_code,
    )


def create_error_response(*, error: str, error_message: str, status_code: int) -> ApiResponse[None]:
    """Создаёт непротиворечивый error response с фактическим HTTP status.

    Args:
        error: Стабильный machine-readable код ошибки.
        error_message: Безопасное описание без внутренних деталей сервиса.
        status_code: Фактический HTTP error status, который вернёт transport layer.

    Returns:
        Validated error envelope без result payload.

    Raises:
        ValidationError: Аргументы нарушают error response invariants.
    """
    return ApiResponse[None](
        ok=False,
        result=None,
        error=error,
        error_message=error_message,
        status_code=status_code,
    )

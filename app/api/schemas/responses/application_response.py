"""Single public response envelope."""

from __future__ import annotations

from typing import Generic, Self

from pydantic import Field, model_validator
from typing_extensions import TypeVar

from api.schemas.base import ResponseModel

# Python 3.12 compatibility: native generic defaults require Python 3.13+.
ResultT = TypeVar("ResultT", default=None)


class ApplicationResponse(ResponseModel, Generic[ResultT]):
    """Represent either a successful result or a safe error."""

    ok: bool = Field(description="Whether the request completed successfully.")
    result: ResultT | None = Field(default=None, description="Successful response payload.")
    error: str | None = Field(
        default=None,
        description="Stable machine-readable error code.",
    )
    error_message: str | None = Field(
        default=None,
        description="Client-safe error message.",
    )

    @model_validator(mode="after")
    def validate_state(self) -> Self:
        """Reject contradictory success and error states."""
        if self.ok:
            if self.error is not None or self.error_message is not None:
                raise ValueError("successful response cannot contain error information")
        elif self.result is not None or not self.error or not self.error_message:
            raise ValueError("error response must contain only error information")
        return self

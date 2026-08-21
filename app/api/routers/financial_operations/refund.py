"""Refund financial operation HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.financial_operations.dependencies import (
    provide_refund_financial_operation,
)
from api.schemas.orm import RefundOperationSchema
from api.schemas.requests import RefundOperationRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.financial_operations import RefundOperationHandler

router = APIRouter()


@router.post(
    path=".refundOperation",
    response_model=ApplicationResponse[RefundOperationSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Fully compensate a financial operation",
    description=(
        "Append a complete immutable REVERSAL and refund audit. The original journal and "
        "business lifecycle remain unchanged; partial refunds are unsupported."
    ),
    operation_id="financial_operations_refund_operation",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_409_CONFLICT: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def refund_financial_operation(
    request: RefundOperationRequest,
    handler: Annotated[
        RefundOperationHandler,
        Depends(provide_refund_financial_operation),
    ],
) -> HandlerResult:
    """Delegate full compensation to the application layer."""
    result = await handler.execute(request.to_command())
    return {
        "ok": True,
        "result": result,
    }

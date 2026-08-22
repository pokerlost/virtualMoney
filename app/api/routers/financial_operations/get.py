"""Get financial operation HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.financial_operations.dependencies import provide_get_financial_operation
from api.schemas.requests import GetOperationRequest
from api.schemas.responses import ApplicationResponse, FinancialOperationResponse
from api.types import HandlerResult
from application.financial_operations import GetOperationHandler

router = APIRouter()


@router.post(
    path=".getOperation",
    response_model=ApplicationResponse[FinancialOperationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get a financial operation",
    description=(
        "Return source-discriminated information from immutable hold, table, rake, refund, "
        "or ledger records without exposing internal fingerprints."
    ),
    operation_id="financial_operations_get_operation",
    openapi_extra={
        "x-pokerlost-authz": {
            "actors": ["service"],
            "permissions": ["financial_operations_get_operation"],
    },
    },
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def get_financial_operation(
    request: GetOperationRequest,
    handler: Annotated[
        GetOperationHandler,
        Depends(provide_get_financial_operation),
    ],
) -> HandlerResult:
    """Delegate source-discriminated audit lookup to the application layer."""
    result = await handler.execute(request.to_query())
    return {
        "ok": True,
        "result": result,
    }

"""Get table-position operations HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.table_positions.dependencies import provide_get_position_operations
from api.schemas.requests import GetOperationsRequest
from api.schemas.responses import (
    ApplicationResponse,
    PaginationResponse,
    TablePositionOperationResponse,
)
from api.types import HandlerResult
from application.table_positions import GetOperationsHandler

router = APIRouter()


@router.post(
    path=".getOperations",
    response_model=ApplicationResponse[PaginationResponse[TablePositionOperationResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get table-position operations",
    description=(
        "Return a descending keyset page of immutable BuyIn, ReBuy, and CashOut "
        "audits. "
        "This is not poker hand history."
    ),
    operation_id="virtualMoney.tablePositions.getOperations",
    openapi_extra={
        "x-pokerlost-authz": {
            "roles": [
                "user",
                "master",
                "auto",
            ],
        },
    },
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def get_table_position_operations(
    request: GetOperationsRequest,
    handler: Annotated[
        GetOperationsHandler,
        Depends(provide_get_position_operations),
    ],
) -> HandlerResult:
    """Delegate bounded operation history to the application layer."""
    result = await handler.execute(request.to_query())
    return {
        "ok": True,
        "result": result,
    }

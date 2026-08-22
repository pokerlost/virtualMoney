"""Table CashOut HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.table_positions.dependencies import provide_cash_out
from api.schemas.orm import PlayerTablePositionSchema
from api.schemas.requests import CashOutRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.table_positions import CashOutHandler

router = APIRouter()


@router.post(
    path=".cashOut",
    response_model=ApplicationResponse[PlayerTablePositionSchema],
    status_code=status.HTTP_200_OK,
    summary="Close a table position",
    description=(
        "Return the authoritative final stack from pooled escrow to the USER account and "
        "close the position. A zero stack creates no zero-value journal."
    ),
    operation_id="table_positions_cash_out",
    openapi_extra={
        "x-pokerlost-authz": {
            "actors": ["service"],
            "permissions": ["table_positions_cash_out"],
    },
    },
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_409_CONFLICT: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def cash_out(
    request: CashOutRequest,
    handler: Annotated[CashOutHandler, Depends(provide_cash_out)],
) -> HandlerResult:
    """Delegate CashOut orchestration to the application layer."""
    result = await handler.execute(request.to_command())
    return {
        "ok": True,
        "result": result,
    }

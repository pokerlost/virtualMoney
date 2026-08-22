"""Table ReBuy HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.table_positions.dependencies import provide_re_buy
from api.schemas.orm import PlayerTablePositionSchema
from api.schemas.requests import ReBuyRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.table_positions import ReBuyHandler

router = APIRouter()


@router.post(
    path=".reBuy",
    response_model=ApplicationResponse[PlayerTablePositionSchema],
    status_code=status.HTTP_200_OK,
    summary="Add funds to an open table position",
    description=(
        "Capture a new ACTIVE hold into the position escrow and increase totalBuyInMinor. "
        "A CLOSED position is never reopened."
    ),
    operation_id="virtualMoney.tablePositions.reBuy",
    openapi_extra={
        "x-pokerlost-authz": {
            "roles": [
                "auto",
            ],
        }
    },
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_409_CONFLICT: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def re_buy(
    request: ReBuyRequest,
    handler: Annotated[ReBuyHandler, Depends(provide_re_buy)],
) -> HandlerResult:
    """Delegate ReBuy orchestration to the application layer."""
    result = await handler.execute(request.to_command())
    return {
        "ok": True,
        "result": result,
    }

"""Table BuyIn HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.table_positions.dependencies import provide_buy_in
from api.schemas.orm import PlayerTablePositionSchema
from api.schemas.requests import BuyInRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.table_positions import BuyInHandler

router = APIRouter()


@router.post(
    path=".buyIn",
    response_model=ApplicationResponse[PlayerTablePositionSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Open a table position",
    description=(
        "Capture an ACTIVE hold in full, move its amount to pooled table escrow, and create "
        "one OPEN durable position atomically."
    ),
    operation_id="table_positions_buy_in",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_409_CONFLICT: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def buy_in(
    request: BuyInRequest,
    handler: Annotated[BuyInHandler, Depends(provide_buy_in)],
) -> HandlerResult:
    """Delegate BuyIn orchestration to the application layer."""
    result = await handler.execute(request.to_command())
    return {
        "ok": True,
        "result": result,
    }

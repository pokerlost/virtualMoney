"""Get table position HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.table_positions.dependencies import provide_get_position
from api.schemas.orm import PlayerTablePositionSchema
from api.schemas.requests import GetPositionRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.table_positions import GetPositionHandler

router = APIRouter()


@router.post(
    path=".getPosition",
    response_model=ApplicationResponse[PlayerTablePositionSchema],
    status_code=status.HTTP_200_OK,
    summary="Get a table position",
    description=(
        "Return the durable OPEN or CLOSED financial lifecycle. This is not a live poker stack."
    ),
    operation_id="table_positions_get_position",
    openapi_extra={
        "x-pokerlost-authz": {
            "actors": ["service"],
            "permissions": ["table_positions_get_position"],
    },
    },
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def get_player_table_position(
    request: GetPositionRequest,
    handler: Annotated[GetPositionHandler, Depends(provide_get_position)],
) -> HandlerResult:
    """Delegate durable position lookup to the application layer."""
    result = await handler.execute(request.to_query())
    return {
        "ok": True,
        "result": result,
    }

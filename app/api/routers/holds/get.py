"""Get hold HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.holds.dependencies import provide_get_hold
from api.schemas.orm import HoldSchema
from api.schemas.requests import GetHoldRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.holds import GetHoldHandler

router = APIRouter()


@router.post(
    path=".getHold",
    response_model=ApplicationResponse[HoldSchema],
    status_code=status.HTTP_200_OK,
    summary="Get a funds hold",
    description="Return the current full-only hold lifecycle state.",
    operation_id="holds_get_hold",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
    },
)
async def get_hold(
    request: GetHoldRequest,
    handler: Annotated[GetHoldHandler, Depends(provide_get_hold)],
) -> HandlerResult:
    """Delegate hold lookup to the application layer."""
    result = await handler.execute(request.to_query())
    return {
        "ok": True,
        "result": result,
    }

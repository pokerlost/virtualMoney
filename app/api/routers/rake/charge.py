"""Charge rake HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.rake.dependencies import provide_charge_rake
from api.schemas.orm import RakeOperationSchema
from api.schemas.requests import ChargeRakeRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.rake import ChargeRakeHandler

router = APIRouter()


@router.post(
    path=".chargeRake",
    response_model=ApplicationResponse[RakeOperationSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Charge rake for a completed poker hand",
    description=(
        "Transfer a positive rake amount calculated by Poker Server from table escrow to the "
        "single system RAKE account for the asset."
    ),
    operation_id="virtualMoney.rake.chargeRake",
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
async def charge_rake(
    request: ChargeRakeRequest,
    handler: Annotated[ChargeRakeHandler, Depends(provide_charge_rake)],
) -> HandlerResult:
    """Delegate escrow-to-rake posting to the application layer."""
    result = await handler.execute(request.to_command())
    return {
        "ok": True,
        "result": result,
    }

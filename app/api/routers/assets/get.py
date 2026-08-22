"""Get asset by UUID HTTP action."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.routers.assets.dependencies import provide_get_asset
from api.schemas.orm import AssetSchema
from api.schemas.requests import GetAssetRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.assets import GetAssetHandler

router = APIRouter()


@router.post(
    path=".getAsset",
    response_model=ApplicationResponse[AssetSchema],
    status_code=status.HTTP_200_OK,
    summary="Get an asset",
    description="Return internal financial asset metadata by its service-owned UUID.",
    operation_id="virtualMoney.assets.getAsset",
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
async def get_asset(
    request: GetAssetRequest,
    handler: Annotated[GetAssetHandler, Depends(provide_get_asset)],
) -> HandlerResult:
    """Delegate asset lookup to the application layer."""
    result = await handler.execute(request.to_query())
    return {
        "ok": True,
        "result": result,
    }

"""Liveness and enabled-dependency readiness routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from virtualmoney.resources import ApplicationResources, get_resources

router = APIRouter(include_in_schema=False)


@router.get("/health/live")
async def live() -> dict[str, str]:
    """Confirm the process can answer HTTP without querying dependencies."""
    return {"status": "alive"}


@router.get("/health/ready")
async def ready(
    resources: Annotated[ApplicationResources, Depends(get_resources)],
) -> dict[str, str]:
    """Check only resources enabled for this application."""
    if not resources.ready:
        raise HTTPException(status_code=503, detail="Required dependency unavailable")
    return {"status": "ready"}

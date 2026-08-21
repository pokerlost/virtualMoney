"""Typed access to lifespan-owned runtime resources."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from api.resources import ApplicationResources


def get_application_resources(request: Request) -> ApplicationResources:
    """Return initialized resources from FastAPI state."""
    resources = request.app.state.resources
    if not isinstance(resources, ApplicationResources):
        raise RuntimeError("application resources are not initialized")
    return resources


type ApplicationResourcesDep = Annotated[
    ApplicationResources,
    Depends(get_application_resources),
]

"""Typed, lifespan-owned process resources and narrow request access."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request


@dataclass(frozen=True, slots=True)
class ApplicationResources:
    """Resources owned by exactly one ASGI lifespan and worker."""

    ready: bool = True


def getResources(request: Request) -> ApplicationResources:
    """Expose initialized resources through one narrow dependency."""
    resources = getattr(request.app.state, "resources", None)
    if not isinstance(resources, ApplicationResources):
        raise RuntimeError("Application resources are not initialized")
    return resources

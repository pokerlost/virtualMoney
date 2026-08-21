"""Base model for validated SQLAlchemy mapping projections."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ProjectionModel(BaseModel):
    """Keep database read shapes immutable and explicitly labeled."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=True,
    )

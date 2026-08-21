"""Immutable base for internal structured value models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ValueModel(BaseModel):
    """Provide strict field ownership for application and domain values."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
        validate_default=True,
    )

"""Shared configuration for public API models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class APIModel(BaseModel):
    """Apply camelCase aliases and strict public-field behavior."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        extra="forbid",
        serialize_by_alias=True,
        str_strip_whitespace=True,
        validate_default=True,
        validate_by_alias=True,
        validate_by_name=True,
    )

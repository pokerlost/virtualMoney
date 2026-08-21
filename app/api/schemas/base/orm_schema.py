"""Base model for attribute-compatible entity responses."""

from __future__ import annotations

from pydantic import ConfigDict

from .response_model import ResponseModel


class ORMSchema(ResponseModel):
    """Enable explicit attribute-based entity serialization."""

    model_config = ConfigDict(from_attributes=True)

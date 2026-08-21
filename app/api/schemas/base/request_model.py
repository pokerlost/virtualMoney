"""Base model for JSON request bodies."""

from __future__ import annotations

from .api_model import APIModel


class RequestModel(APIModel):
    """Define the strict camelCase request boundary."""

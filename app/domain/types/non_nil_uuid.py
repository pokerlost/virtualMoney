"""Reusable non-nil UUID type."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator


def _reject_nil_uuid(value: UUID) -> UUID:
    if value.int == 0:
        raise ValueError("identifier must not be a nil UUID")
    return value


type NonNilUUID = Annotated[UUID, AfterValidator(_reject_nil_uuid)]

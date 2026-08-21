"""Decoded keyset cursor."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID, UtcDatetime


class PaginationCursor(ValueModel):
    """Internal descending timestamp and UUID keyset position."""

    occurred_at: UtcDatetime
    item_id: NonNilUUID

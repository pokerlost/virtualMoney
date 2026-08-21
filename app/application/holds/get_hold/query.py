"""Hold lookup query."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID


class GetHoldQuery(ValueModel):
    """Identify one funds hold for lookup."""

    hold_id: NonNilUUID

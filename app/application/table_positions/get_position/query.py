"""Table position lookup query."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID


class GetPositionQuery(ValueModel):
    """Identify one durable table position for lookup."""

    position_id: NonNilUUID

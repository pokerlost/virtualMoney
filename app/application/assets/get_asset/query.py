"""Asset lookup query."""

from __future__ import annotations

from domain import ValueModel
from domain.types import NonNilUUID


class GetAssetQuery(ValueModel):
    """Identify one financial asset for lookup."""

    asset_id: NonNilUUID

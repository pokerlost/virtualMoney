"""Asset code lookup query."""

from __future__ import annotations

from domain import ValueModel
from domain.types import AssetCode


class GetAssetByCodeQuery(ValueModel):
    """Identify one financial asset by canonical code."""

    code: AssetCode

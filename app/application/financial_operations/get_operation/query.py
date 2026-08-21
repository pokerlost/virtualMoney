"""Financial operation lookup query."""

from __future__ import annotations

from domain import ValueModel
from domain.types import OperationId


class GetOperationQuery(ValueModel):
    """Identify one immutable operation across financial sources."""

    operation_id: OperationId

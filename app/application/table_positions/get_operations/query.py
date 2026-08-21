"""Table position operation history query."""

from __future__ import annotations

from application.pagination import PaginationInput
from domain import ValueModel
from domain.types import NonNilUUID


class GetOperationsQuery(ValueModel):
    """Describe one bounded page of table-position operations."""

    position_id: NonNilUUID
    pagination: PaginationInput

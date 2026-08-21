"""Immutable operation identity persistence mixin."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column


class OperationIdentityMixin:
    """Provide stable operation identity and semantic payload fingerprint."""

    operation_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    payload_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)

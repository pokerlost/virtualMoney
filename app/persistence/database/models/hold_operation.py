"""SQLAlchemy mapping for an immutable hold operation."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums import HoldOperationType
from persistence.database import UUIDModel
from persistence.database.mixins import CreatedAtMixin, OperationIdentityMixin

if TYPE_CHECKING:
    from .hold import HoldModel
    from .ledger_transaction import LedgerTransactionModel


class HoldOperationModel(CreatedAtMixin, OperationIdentityMixin, UUIDModel):
    """Append-only persisted audit/idempotency record hold mutation."""

    __tablename__ = "hold_operations"
    __table_args__ = (
        CheckConstraint(
            "operation_id <> '00000000-0000-0000-0000-000000000000'::uuid",
            name="ck_hold_operations_operation_id_not_nil",
        ),
        CheckConstraint(
            "operation_type IN ('RESERVE', 'RELEASE', 'CAPTURE')",
            name="ck_hold_operations_operation_type",
        ),
        CheckConstraint(
            "payload_fingerprint ~ '^[0-9a-f]{64}$'",
            name="ck_hold_operations_payload_fingerprint",
        ),
        CheckConstraint(
            "(operation_type IN ('RESERVE', 'RELEASE') "
            "AND ledger_transaction_id IS NULL) OR "
            "(operation_type = 'CAPTURE' AND ledger_transaction_id IS NOT NULL)",
            name="ck_hold_operations_ledger_link",
        ),
        UniqueConstraint("operation_id", name="uq_hold_operations_operation_id"),
        UniqueConstraint(
            "ledger_transaction_id",
            name="uq_hold_operations_ledger_transaction_id",
        ),
        Index("ix_hold_operations_hold_id", "hold_id"),
    )

    hold_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("holds.id", ondelete="RESTRICT"),
        nullable=False,
    )
    operation_type: Mapped[HoldOperationType] = mapped_column(
        SqlEnum(
            HoldOperationType,
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            length=16,
        ),
        nullable=False,
    )
    ledger_transaction_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ledger_transactions.id",
            name="fk_hold_operations_ledger_transaction_id_ledger_transactions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    hold: Mapped[HoldModel] = relationship(
        back_populates="operations",
        lazy="raise",
    )
    ledger_transaction: Mapped[LedgerTransactionModel | None] = relationship(
        foreign_keys=[ledger_transaction_id],
        lazy="raise",
    )

"""SQLAlchemy mapping for a financial hold."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums import HoldStatus
from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin

if TYPE_CHECKING:
    from .account import AccountModel
    from .hold_operation import HoldOperationModel
    from .ledger_transaction import LedgerTransactionModel


class HoldModel(TimestampMixin, UUIDModel):
    """Persistence state of a full hold on one account."""

    __tablename__ = "holds"
    __table_args__ = (
        CheckConstraint("amount_minor > 0", name="ck_holds_amount_positive"),
        CheckConstraint(
            "status IN ('ACTIVE', 'RELEASED', 'CAPTURED')",
            name="ck_holds_status",
        ),
        CheckConstraint(
            "(reference_type IS NULL AND reference_id IS NULL) OR "
            "(reference_type IS NOT NULL AND reference_id IS NOT NULL)",
            name="ck_holds_reference_pair",
        ),
        CheckConstraint(
            "reference_type IS NULL OR reference_type ~ '^[A-Z][A-Z0-9_]{0,63}$'",
            name="ck_holds_reference_type",
        ),
        CheckConstraint(
            "reference_id IS NULL OR reference_id <> '00000000-0000-0000-0000-000000000000'::uuid",
            name="ck_holds_reference_id_not_nil",
        ),
        CheckConstraint(
            "(status = 'ACTIVE' AND released_at IS NULL AND captured_at IS NULL "
            "AND capture_ledger_transaction_id IS NULL) OR "
            "(status = 'RELEASED' AND released_at IS NOT NULL AND captured_at IS NULL "
            "AND capture_ledger_transaction_id IS NULL) OR "
            "(status = 'CAPTURED' AND released_at IS NULL AND captured_at IS NOT NULL "
            "AND capture_ledger_transaction_id IS NOT NULL)",
            name="ck_holds_status_metadata",
        ),
        CheckConstraint("updated_at >= created_at", name="ck_holds_updated_at"),
        CheckConstraint(
            "released_at IS NULL OR (released_at >= created_at AND released_at <= updated_at)",
            name="ck_holds_released_at",
        ),
        CheckConstraint(
            "captured_at IS NULL OR (captured_at >= created_at AND captured_at <= updated_at)",
            name="ck_holds_captured_at",
        ),
        UniqueConstraint(
            "capture_ledger_transaction_id",
            name="uq_holds_capture_ledger_transaction_id",
        ),
        Index("ix_holds_account_status", "account_id", "status"),
    )

    account_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[HoldStatus] = mapped_column(
        SqlEnum(
            HoldStatus,
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            length=16,
        ),
        nullable=False,
    )
    reference_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reference_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=True,
    )
    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    captured_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    capture_ledger_transaction_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ledger_transactions.id",
            name="fk_holds_capture_ledger_transaction_id_ledger_transactions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    account: Mapped[AccountModel] = relationship(
        back_populates="holds",
        lazy="raise",
    )
    operations: Mapped[list[HoldOperationModel]] = relationship(
        back_populates="hold",
        lazy="raise",
        order_by="HoldOperationModel.created_at",
    )
    capture_transaction: Mapped[LedgerTransactionModel | None] = relationship(
        foreign_keys=[capture_ledger_transaction_id],
        lazy="raise",
    )

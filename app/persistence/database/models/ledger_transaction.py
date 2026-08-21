"""SQLAlchemy mapping for an immutable ledger transaction."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums import LedgerTransactionStatus, LedgerTransactionType
from persistence.database import UUIDModel
from persistence.database.mixins import CreatedAtMixin, OperationIdentityMixin

if TYPE_CHECKING:
    from .ledger_entry import LedgerEntryModel


class LedgerTransactionModel(CreatedAtMixin, OperationIdentityMixin, UUIDModel):
    """Persistence representation of one immutable posted journal."""

    __tablename__ = "ledger_transactions"
    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('ADJUSTMENT', 'CASH_OUT', 'HOLD_CAPTURE', 'RAKE', 'REVERSAL')",
            name="ck_ledger_transactions_transaction_type",
        ),
        CheckConstraint(
            "status = 'POSTED'",
            name="ck_ledger_transactions_status",
        ),
        CheckConstraint(
            "payload_fingerprint ~ '^[0-9a-f]{64}$'",
            name="ck_ledger_transactions_payload_fingerprint",
        ),
        CheckConstraint(
            "operation_id <> '00000000-0000-0000-0000-000000000000'::uuid",
            name="ck_ledger_transactions_operation_id_not_nil",
        ),
        CheckConstraint(
            "(reference_type IS NULL AND reference_id IS NULL) OR "
            "(reference_type IS NOT NULL AND reference_id IS NOT NULL)",
            name="ck_ledger_transactions_reference_pair",
        ),
        CheckConstraint(
            "reference_type IS NULL OR reference_type ~ '^[A-Z][A-Z0-9_]{0,63}$'",
            name="ck_ledger_transactions_reference_type",
        ),
        CheckConstraint(
            "reference_id IS NULL OR reference_id <> '00000000-0000-0000-0000-000000000000'::uuid",
            name="ck_ledger_transactions_reference_id_not_nil",
        ),
        CheckConstraint(
            "description IS NULL OR char_length(btrim(description)) BETWEEN 1 AND 500",
            name="ck_ledger_transactions_description",
        ),
        CheckConstraint(
            "(transaction_type IN ('ADJUSTMENT', 'CASH_OUT', 'HOLD_CAPTURE', 'RAKE') "
            "AND reversal_of_transaction_id IS NULL) OR "
            "(transaction_type = 'REVERSAL' AND reversal_of_transaction_id IS NOT NULL)",
            name="ck_ledger_transactions_reversal_type",
        ),
        CheckConstraint(
            "reversal_of_transaction_id IS NULL OR reversal_of_transaction_id <> id",
            name="ck_ledger_transactions_not_self_reversal",
        ),
        CheckConstraint(
            "reversal_of_transaction_id IS NULL OR "
            "reversal_of_transaction_id <> '00000000-0000-0000-0000-000000000000'::uuid",
            name="ck_ledger_transactions_reversal_id_not_nil",
        ),
        CheckConstraint(
            "posted_at >= created_at",
            name="ck_ledger_transactions_posted_at",
        ),
        UniqueConstraint("operation_id", name="uq_ledger_transactions_operation_id"),
        UniqueConstraint(
            "reversal_of_transaction_id",
            name="uq_ledger_transactions_reversal_of_transaction_id",
        ),
        Index(
            "ix_ledger_transactions_posted_at_id",
            "posted_at",
            "id",
        ),
    )

    asset_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
    )
    transaction_type: Mapped[LedgerTransactionType] = mapped_column(
        SqlEnum(
            LedgerTransactionType,
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            length=32,
        ),
        nullable=False,
    )
    status: Mapped[LedgerTransactionStatus] = mapped_column(
        SqlEnum(
            LedgerTransactionStatus,
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
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reversal_of_transaction_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ledger_transactions.id",
            name="fk_ledger_transactions_reversal_id_ledger_transactions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    posted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    entries: Mapped[list[LedgerEntryModel]] = relationship(
        back_populates="ledger_transaction",
        cascade="save-update, merge",
        lazy="raise",
        order_by="LedgerEntryModel.sequence",
    )
    original_transaction: Mapped[LedgerTransactionModel | None] = relationship(
        back_populates="reversal_transaction",
        foreign_keys="LedgerTransactionModel.reversal_of_transaction_id",
        remote_side="LedgerTransactionModel.id",
        lazy="raise",
    )
    reversal_transaction: Mapped[LedgerTransactionModel | None] = relationship(
        back_populates="original_transaction",
        foreign_keys="LedgerTransactionModel.reversal_of_transaction_id",
        lazy="raise",
        uselist=False,
    )

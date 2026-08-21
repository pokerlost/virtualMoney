"""Typed SQLAlchemy RefundOperation append-only audit mapping."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.database import UUIDModel
from persistence.database.mixins import CreatedAtMixin, OperationIdentityMixin

if TYPE_CHECKING:
    from .ledger_transaction import LedgerTransactionModel


class RefundOperationModel(CreatedAtMixin, OperationIdentityMixin, UUIDModel):
    """Persistence representation full compensation audit."""

    __tablename__ = "refund_operations"
    __table_args__ = (
        CheckConstraint(
            "operation_id <> '00000000-0000-0000-0000-000000000000'::uuid",
            name="ck_refund_operations_operation_id_not_nil",
        ),
        CheckConstraint(
            "target_operation_id <> '00000000-0000-0000-0000-000000000000'::uuid",
            name="ck_refund_operations_target_operation_id_not_nil",
        ),
        CheckConstraint(
            "original_ledger_transaction_id <> reversal_ledger_transaction_id",
            name="ck_refund_operations_transactions_different",
        ),
        CheckConstraint(
            "char_length(btrim(reason)) BETWEEN 1 AND 500",
            name="ck_refund_operations_reason",
        ),
        CheckConstraint(
            "payload_fingerprint ~ '^[0-9a-f]{64}$'",
            name="ck_refund_operations_payload_fingerprint",
        ),
        UniqueConstraint("operation_id", name="uq_refund_operations_operation_id"),
        UniqueConstraint(
            "target_operation_id",
            name="uq_refund_operations_target_operation_id",
        ),
        UniqueConstraint(
            "original_ledger_transaction_id",
            name="uq_refund_operations_original_ledger_transaction_id",
        ),
        UniqueConstraint(
            "reversal_ledger_transaction_id",
            name="uq_refund_operations_reversal_ledger_transaction_id",
        ),
    )

    target_operation_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=False,
    )
    original_ledger_transaction_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ledger_transactions.id",
            name="fk_refund_operations_original_ledger_transaction_id_ledger",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    reversal_ledger_transaction_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ledger_transactions.id",
            name="fk_refund_operations_reversal_ledger_transaction_id_ledger",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    original_transaction: Mapped[LedgerTransactionModel] = relationship(
        foreign_keys=[original_ledger_transaction_id],
        lazy="raise",
    )
    reversal_transaction: Mapped[LedgerTransactionModel] = relationship(
        foreign_keys=[reversal_ledger_transaction_id],
        lazy="raise",
    )

"""SQLAlchemy mapping for an immutable table-money operation."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    BigInteger,
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

from domain.enums import TableMoneyOperationType
from persistence.database import UUIDModel
from persistence.database.mixins import CreatedAtMixin, OperationIdentityMixin

if TYPE_CHECKING:
    from .hold import HoldModel
    from .ledger_transaction import LedgerTransactionModel
    from .player_table_position import PlayerTablePositionModel


class TableMoneyOperationModel(CreatedAtMixin, OperationIdentityMixin, UUIDModel):
    """Append-only high-level table money audit/idempotency row."""

    __tablename__ = "table_money_operations"
    __table_args__ = (
        CheckConstraint(
            "operation_id <> '00000000-0000-0000-0000-000000000000'::uuid",
            name="ck_table_money_operations_operation_id_not_nil",
        ),
        CheckConstraint(
            "operation_type IN ('BUY_IN', 'REBUY', 'CASH_OUT')",
            name="ck_table_money_operations_operation_type",
        ),
        CheckConstraint(
            "payload_fingerprint ~ '^[0-9a-f]{64}$'",
            name="ck_table_money_operations_payload_fingerprint",
        ),
        CheckConstraint(
            "amount_minor >= 0",
            name="ck_table_money_operations_amount_non_negative",
        ),
        CheckConstraint(
            "(operation_type IN ('BUY_IN', 'REBUY') AND amount_minor > 0 "
            "AND hold_id IS NOT NULL AND ledger_transaction_id IS NOT NULL) OR "
            "(operation_type = 'CASH_OUT' AND hold_id IS NULL AND "
            "((amount_minor = 0 AND ledger_transaction_id IS NULL) OR "
            "(amount_minor > 0 AND ledger_transaction_id IS NOT NULL)))",
            name="ck_table_money_operations_financial_links",
        ),
        UniqueConstraint("operation_id", name="uq_table_money_operations_operation_id"),
        UniqueConstraint("hold_id", name="uq_table_money_operations_hold_id"),
        UniqueConstraint(
            "ledger_transaction_id",
            name="uq_table_money_operations_ledger_transaction_id",
        ),
        Index(
            "ix_table_money_operations_position_created_id",
            "position_id",
            "created_at",
            "operation_id",
        ),
    )

    position_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("player_table_positions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    operation_type: Mapped[TableMoneyOperationType] = mapped_column(
        SqlEnum(
            TableMoneyOperationType,
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            length=16,
        ),
        nullable=False,
    )
    hold_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("holds.id", ondelete="RESTRICT"),
        nullable=True,
    )
    ledger_transaction_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ledger_transactions.id",
            name="fk_table_money_operations_ledger_transaction_id_ledger",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    position: Mapped[PlayerTablePositionModel] = relationship(
        back_populates="operations",
        lazy="raise",
    )
    hold: Mapped[HoldModel | None] = relationship(
        foreign_keys=[hold_id],
        lazy="raise",
    )
    ledger_transaction: Mapped[LedgerTransactionModel | None] = relationship(
        foreign_keys=[ledger_transaction_id],
        lazy="raise",
    )

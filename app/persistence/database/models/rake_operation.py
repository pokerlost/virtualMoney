"""Typed SQLAlchemy RakeOperation append-only audit mapping."""

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
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.database import UUIDModel
from persistence.database.mixins import CreatedAtMixin, OperationIdentityMixin

if TYPE_CHECKING:
    from .account import AccountModel
    from .asset import AssetModel
    from .ledger_transaction import LedgerTransactionModel


class RakeOperationModel(CreatedAtMixin, OperationIdentityMixin, UUIDModel):
    """Persistence representation completed escrow-to-rake operation."""

    __tablename__ = "rake_operations"
    __table_args__ = (
        CheckConstraint(
            "operation_id <> '00000000-0000-0000-0000-000000000000'::uuid",
            name="ck_rake_operations_operation_id_not_nil",
        ),
        CheckConstraint(
            "table_id <> '00000000-0000-0000-0000-000000000000'::uuid",
            name="ck_rake_operations_table_id_not_nil",
        ),
        CheckConstraint(
            "hand_id <> '00000000-0000-0000-0000-000000000000'::uuid",
            name="ck_rake_operations_hand_id_not_nil",
        ),
        CheckConstraint(
            "amount_minor > 0",
            name="ck_rake_operations_amount_positive",
        ),
        CheckConstraint(
            "table_escrow_account_id <> rake_account_id",
            name="ck_rake_operations_accounts_different",
        ),
        CheckConstraint(
            "payload_fingerprint ~ '^[0-9a-f]{64}$'",
            name="ck_rake_operations_payload_fingerprint",
        ),
        UniqueConstraint("operation_id", name="uq_rake_operations_operation_id"),
        UniqueConstraint(
            "ledger_transaction_id",
            name="uq_rake_operations_ledger_transaction_id",
        ),
        Index(
            "ix_rake_operations_table_hand",
            "table_id",
            "hand_id",
        ),
    )

    table_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    hand_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    asset_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
    )
    table_escrow_account_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "accounts.id",
            name="fk_rake_operations_table_escrow_account_id_accounts",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    rake_account_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "accounts.id",
            name="fk_rake_operations_rake_account_id_accounts",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ledger_transaction_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ledger_transactions.id",
            name="fk_rake_operations_ledger_transaction_id_ledger_transactions",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    asset: Mapped[AssetModel] = relationship(
        foreign_keys=[asset_id],
        lazy="raise",
    )
    table_escrow_account: Mapped[AccountModel] = relationship(
        foreign_keys=[table_escrow_account_id],
        lazy="raise",
    )
    rake_account: Mapped[AccountModel] = relationship(
        foreign_keys=[rake_account_id],
        lazy="raise",
    )
    ledger_transaction: Mapped[LedgerTransactionModel] = relationship(
        foreign_keys=[ledger_transaction_id],
        lazy="raise",
    )

"""SQLAlchemy 2.x mapping for a financial Account."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    UniqueConstraint,
    text,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums import AccountStatus, AccountType, OwnerType
from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin

if TYPE_CHECKING:
    from .account_balance import AccountBalanceModel
    from .hold import HoldModel
    from .ledger_entry import LedgerEntryModel


class AccountModel(TimestampMixin, UUIDModel):
    """Persistence representation of a financial account without mutable balance."""

    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint(
            "account_type IN ('USER', 'TREASURY', 'RAKE', 'TABLE_ESCROW')",
            name="ck_accounts_account_type",
        ),
        CheckConstraint(
            "owner_type IN ('USER', 'TABLE', 'SYSTEM')",
            name="ck_accounts_owner_type",
        ),
        CheckConstraint(
            "(owner_type = 'SYSTEM' AND owner_id IS NULL) OR "
            "(owner_type IN ('USER', 'TABLE') AND owner_id IS NOT NULL AND "
            "owner_id <> '00000000-0000-0000-0000-000000000000'::uuid)",
            name="ck_accounts_owner_id_semantics",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'FROZEN', 'CLOSED')",
            name="ck_accounts_status",
        ),
        CheckConstraint(
            "(account_type = 'USER' AND owner_type = 'USER') OR "
            "(account_type = 'TABLE_ESCROW' AND owner_type = 'TABLE') OR "
            "(account_type IN ('TREASURY', 'RAKE') AND owner_type = 'SYSTEM')",
            name="ck_accounts_owner_matches_type",
        ),
        UniqueConstraint(
            "owner_type",
            "owner_id",
            "asset_id",
            "account_type",
            name="uq_accounts_owner_asset_type",
        ),
        Index(
            "uq_accounts_rake_asset",
            "asset_id",
            unique=True,
            postgresql_where=text("account_type = 'RAKE'"),
        ),
        Index(
            "uq_accounts_treasury_asset",
            "asset_id",
            unique=True,
            postgresql_where=text("account_type = 'TREASURY'"),
        ),
        Index("ix_accounts_asset_id", "asset_id"),
    )

    asset_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
    )
    account_type: Mapped[AccountType] = mapped_column(
        SqlEnum(
            AccountType,
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            length=32,
        ),
        nullable=False,
    )
    owner_type: Mapped[OwnerType] = mapped_column(
        SqlEnum(
            OwnerType,
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            length=16,
        ),
        nullable=False,
    )
    owner_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=True,
    )
    status: Mapped[AccountStatus] = mapped_column(
        SqlEnum(
            AccountStatus,
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            length=16,
        ),
        nullable=False,
    )
    balance: Mapped[AccountBalanceModel] = relationship(
        back_populates="account",
        lazy="raise",
        uselist=False,
    )
    holds: Mapped[list[HoldModel]] = relationship(
        back_populates="account",
        lazy="raise",
    )
    ledger_entries: Mapped[list[LedgerEntryModel]] = relationship(
        back_populates="account",
        lazy="raise",
    )

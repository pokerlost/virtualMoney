"""SQLAlchemy mapping for a durable player table position."""

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
    text,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums import PlayerTablePositionStatus
from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin

if TYPE_CHECKING:
    from .account import AccountModel
    from .table_money_operation import TableMoneyOperationModel


class PlayerTablePositionModel(TimestampMixin, UUIDModel):
    """Persistence state of one player's durable financial table lifecycle."""

    __tablename__ = "player_table_positions"
    __table_args__ = (
        CheckConstraint(
            "user_id <> '00000000-0000-0000-0000-000000000000'::uuid",
            name="ck_player_table_positions_user_id_not_nil",
        ),
        CheckConstraint(
            "table_id <> '00000000-0000-0000-0000-000000000000'::uuid",
            name="ck_player_table_positions_table_id_not_nil",
        ),
        CheckConstraint(
            "status IN ('OPEN', 'CLOSED')",
            name="ck_player_table_positions_status",
        ),
        CheckConstraint(
            "total_buy_in_minor > 0",
            name="ck_player_table_positions_buy_in_positive",
        ),
        CheckConstraint(
            "total_cash_out_minor >= 0",
            name="ck_player_table_positions_cash_out_non_negative",
        ),
        CheckConstraint(
            "user_account_id <> table_escrow_account_id",
            name="ck_player_table_positions_accounts_different",
        ),
        CheckConstraint(
            "(status = 'OPEN' AND total_cash_out_minor = 0 AND closed_at IS NULL) OR "
            "(status = 'CLOSED' AND closed_at IS NOT NULL)",
            name="ck_player_table_positions_status_metadata",
        ),
        CheckConstraint(
            "updated_at >= created_at",
            name="ck_player_table_positions_updated_at",
        ),
        CheckConstraint(
            "closed_at IS NULL OR (closed_at >= created_at AND closed_at <= updated_at)",
            name="ck_player_table_positions_closed_at",
        ),
        Index("ix_player_table_positions_user_id", "user_id"),
        Index("ix_player_table_positions_table_id", "table_id"),
        Index(
            "uq_player_table_positions_open_user_table_asset",
            "user_id",
            "table_id",
            "asset_id",
            unique=True,
            postgresql_where=text("status = 'OPEN'"),
        ),
    )

    user_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    table_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    asset_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
    )
    user_account_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    table_escrow_account_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[PlayerTablePositionStatus] = mapped_column(
        SqlEnum(
            PlayerTablePositionStatus,
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            length=16,
        ),
        nullable=False,
    )
    total_buy_in_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    total_cash_out_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    user_account: Mapped[AccountModel] = relationship(
        foreign_keys=[user_account_id],
        lazy="raise",
    )
    table_escrow_account: Mapped[AccountModel] = relationship(
        foreign_keys=[table_escrow_account_id],
        lazy="raise",
    )
    operations: Mapped[list[TableMoneyOperationModel]] = relationship(
        back_populates="position",
        lazy="raise",
        order_by="TableMoneyOperationModel.created_at",
    )

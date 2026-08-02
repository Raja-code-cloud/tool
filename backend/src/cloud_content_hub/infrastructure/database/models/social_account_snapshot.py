"""Immutable social-account health and follower snapshot model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import IMMUTABLE_UAC_CHECK
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.social_account import SocialAccount
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class SocialAccountSnapshot(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Append-only social-account health and follower observation."""

    __tablename__ = "social_account_snapshots"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "social_account_id"],
            ["social_accounts.workspace_id", "social_accounts.id"],
            name="fk_social_account_snapshots__account",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "followers_count IS NULL OR followers_count >= 0",
            name="ck_social_account_snapshots__followers",
        ),
        CheckConstraint(
            "connection_status IN ('connected','disconnected')",
            name="ck_social_account_snapshots__connection_status",
        ),
        CheckConstraint(
            "health_status IN ('healthy','warning','error','needs_reauth')",
            name="ck_social_account_snapshots__health_status",
        ),
        CheckConstraint(IMMUTABLE_UAC_CHECK, name="ck_social_account_snapshots__immutable_uac"),
        UniqueConstraint("workspace_id", "id", name="uq_social_account_snapshots__workspace_id_id"),
        UniqueConstraint(
            "workspace_id",
            "social_account_id",
            "snapshot_at",
            name="uq_social_account_snapshots__account_time",
        ),
        Index(
            "ix_social_account_snapshots__workspace_account_time",
            "workspace_id",
            "social_account_id",
            text("snapshot_at DESC"),
        ),
        {"comment": "Immutable social-account health and follower history."},
    )

    social_account_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    followers_count: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    connection_status: Mapped[str] = mapped_column(Text, nullable=False)
    health_status: Mapped[str] = mapped_column(Text, nullable=False)
    metrics: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="social_account_snapshots",
        lazy="raise",
        overlaps="snapshots",
    )
    social_account: Mapped[SocialAccount] = relationship(
        "SocialAccount",
        back_populates="snapshots",
        lazy="raise",
        overlaps="workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"SocialAccountSnapshot(id={self.id!r}, snapshot_at={self.snapshot_at!r})"

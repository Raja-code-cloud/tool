"""Granted platform scope permission junction model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.social_account import SocialAccount
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class SocialAccountPermission(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Junction recording granted platform scopes for a social account."""

    __tablename__ = "social_account_permissions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "social_account_id"],
            ["social_accounts.workspace_id", "social_accounts.id"],
            name="fk_social_account_permissions__social_account",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "workspace_id", "id", name="uq_social_account_permissions__workspace_id_id"
        ),
        UniqueConstraint(
            "workspace_id",
            "social_account_id",
            "permission_code",
            name="uq_social_account_permissions__account_code",
        ),
        Index(
            "ix_social_account_permissions__workspace_account",
            "workspace_id",
            "social_account_id",
        ),
        {"comment": "Granted platform scope permissions for connected social accounts."},
    )

    social_account_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    permission_code: Mapped[str] = mapped_column(CITEXT(), nullable=False)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="social_account_permissions",
        lazy="raise",
        overlaps="permissions",
    )
    social_account: Mapped[SocialAccount] = relationship(
        "SocialAccount",
        back_populates="permissions",
        lazy="raise",
        overlaps="workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"SocialAccountPermission(id={self.id!r}, permission_code={self.permission_code!r})"

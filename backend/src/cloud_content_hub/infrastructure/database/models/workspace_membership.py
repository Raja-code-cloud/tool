"""Workspace user access membership model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import MembershipStatus
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.membership_role import MembershipRole
    from cloud_content_hub.infrastructure.database.models.user import User
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class WorkspaceMembership(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Workspace-scoped user access separate from organization membership."""

    __tablename__ = "workspace_memberships"
    __table_args__ = (
        CheckConstraint(
            check_in(MembershipStatus, name="status"), name="ck_workspace_memberships__status"
        ),
        UniqueConstraint("workspace_id", "id", name="uq_workspace_memberships__workspace_id_id"),
        Index(
            "ix_workspace_memberships__workspace_status_user",
            "workspace_id",
            "status",
            "user_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "uq_workspace_memberships__workspace_user_where_active",
            "workspace_id",
            "user_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Workspace user access; commercial org membership does not imply access."},
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[MembershipStatus] = mapped_column(
        Text, nullable=False, server_default=text("'active'")
    )
    invited_by: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    invited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="workspace_memberships", lazy="raise"
    )
    user: Mapped[User] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="workspace_memberships",
        lazy="raise",
    )
    inviter: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[invited_by],
        lazy="raise",
    )
    membership_roles: Mapped[list[MembershipRole]] = relationship(
        "MembershipRole",
        back_populates="workspace_membership",
        lazy="raise",
        overlaps="membership_roles,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"WorkspaceMembership(id={self.id!r}, status={self.status!r})"

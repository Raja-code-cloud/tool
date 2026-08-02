"""Organization-level commercial and admin access model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import MembershipStatus, OrganizationRole
from cloud_content_hub.infrastructure.database.mixins import (
    OrganizationMixin,
    UACMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.organization import Organization
    from cloud_content_hub.infrastructure.database.models.user import User


class OrganizationMembership(UUIDPrimaryKeyMixin, OrganizationMixin, UACMixin, Base):
    """Organization-scoped commercial and administrative membership."""

    __tablename__ = "organization_memberships"
    __table_args__ = (
        CheckConstraint(
            check_in(OrganizationRole, name="role"), name="ck_organization_memberships__role"
        ),
        CheckConstraint(
            check_in(MembershipStatus, name="status"), name="ck_organization_memberships__status"
        ),
        Index(
            "ix_organization_memberships__organization_user",
            "organization_id",
            "user_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "uq_organization_memberships__organization_user_where_active",
            "organization_id",
            "user_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {
            "comment": (
                "Organization-level commercial and admin access separate from workspace access."
            ),
        },
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    role: Mapped[OrganizationRole] = mapped_column(Text, nullable=False)
    status: Mapped[MembershipStatus] = mapped_column(
        Text, nullable=False, server_default=text("'active'")
    )
    invited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="organization_memberships", lazy="raise"
    )
    user: Mapped[User] = relationship(
        "User", foreign_keys=[user_id], back_populates="organization_memberships", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"OrganizationMembership(id={self.id!r}, role={self.role!r}, status={self.status!r})"

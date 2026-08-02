"""Role-to-permission grant junction model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import OptionalWorkspaceScopedMixin, UACMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.permission import Permission
    from cloud_content_hub.infrastructure.database.models.role import Role


class RolePermission(OptionalWorkspaceScopedMixin, UACMixin, Base):
    """Junction granting a permission to a system or workspace custom role."""

    __tablename__ = "role_permissions"
    __table_args__ = (
        PrimaryKeyConstraint("role_id", "permission_id", name="pk_role_permissions"),
        Index("ix_role_permissions__role_id", "role_id"),
        Index("ix_role_permissions__permission_id", "permission_id"),
        {"comment": "Permission grants copied with custom roles for workspace RLS."},
    )

    role_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
    )
    permission_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="RESTRICT"),
        nullable=False,
    )

    role: Mapped[Role] = relationship("Role", back_populates="role_permissions", lazy="raise")
    permission: Mapped[Permission] = relationship(
        "Permission", back_populates="role_permissions", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"RolePermission(role_id={self.role_id!r}, permission_id={self.permission_id!r})"

"""System and workspace custom role model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Index, Text, text
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    OptionalWorkspaceScopedMixin,
    UACMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.membership_role import MembershipRole
    from cloud_content_hub.infrastructure.database.models.role_permission import RolePermission
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class Role(UUIDPrimaryKeyMixin, OptionalWorkspaceScopedMixin, UACMixin, Base):
    """Global system role template or workspace-defined custom role."""

    __tablename__ = "roles"
    __table_args__ = (
        CheckConstraint(
            "(is_system AND workspace_id IS NULL) OR (NOT is_system AND workspace_id IS NOT NULL)",
            name="ck_roles__system_workspace_scope",
        ),
        Index(
            "uq_roles__code_where_global_active",
            "code",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND workspace_id IS NULL"),
        ),
        Index(
            "uq_roles__workspace_code_where_active",
            "workspace_id",
            "code",
            unique=True,
            postgresql_nulls_not_distinct=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "System role templates and workspace custom roles."},
    )

    code: Mapped[str] = mapped_column(CITEXT, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    workspace: Mapped[Workspace | None] = relationship(
        "Workspace", back_populates="roles", lazy="raise"
    )
    role_permissions: Mapped[list[RolePermission]] = relationship(
        "RolePermission", back_populates="role", lazy="raise"
    )
    membership_roles: Mapped[list[MembershipRole]] = relationship(
        "MembershipRole", back_populates="role", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Role(id={self.id!r}, code={self.code!r}, is_system={self.is_system!r})"

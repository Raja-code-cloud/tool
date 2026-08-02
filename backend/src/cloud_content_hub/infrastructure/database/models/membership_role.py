"""Workspace membership role assignment junction model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, ForeignKeyConstraint, Index, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import UACMixin, WorkspaceMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.role import Role
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace
    from cloud_content_hub.infrastructure.database.models.workspace_membership import (
        WorkspaceMembership,
    )


class MembershipRole(WorkspaceMixin, UACMixin, Base):
    """Junction assigning system or workspace roles to workspace memberships."""

    __tablename__ = "membership_roles"
    __table_args__ = (
        PrimaryKeyConstraint(
            "workspace_id",
            "membership_id",
            "role_id",
            name="pk_membership_roles",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "membership_id"],
            ["workspace_memberships.workspace_id", "workspace_memberships.id"],
            name="fk_membership_roles__workspace_id_membership_id__workspace_memberships",
            ondelete="CASCADE",
        ),
        Index(
            "ix_membership_roles__workspace_membership",
            "workspace_id",
            "membership_id",
        ),
        Index(
            "ix_membership_roles__workspace_role",
            "workspace_id",
            "role_id",
        ),
        {"comment": "Workspace-local role assignments for workspace memberships."},
    )

    membership_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    role_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
    )

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="membership_roles", lazy="raise"
    )
    workspace_membership: Mapped[WorkspaceMembership] = relationship(
        "WorkspaceMembership",
        foreign_keys="[MembershipRole.membership_id, MembershipRole.workspace_id]",
        back_populates="membership_roles",
        lazy="raise",
        overlaps="workspace",
    )
    role: Mapped[Role] = relationship("Role", back_populates="membership_roles", lazy="raise")

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return (
            f"MembershipRole(workspace_id={self.workspace_id!r}, "
            f"membership_id={self.membership_id!r}, role_id={self.role_id!r})"
        )

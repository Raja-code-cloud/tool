"""Project-level membership and responsibility junction model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import ProjectRole
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.project import Project
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class ProjectMember(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Junction row assigning a user a project-level responsibility role."""

    __tablename__ = "project_members"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "project_id"],
            ["projects.workspace_id", "projects.id"],
            name="fk_project_members__project",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            check_in(ProjectRole, name="project_role"),
            name="ck_project_members__project_role",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_project_members__workspace_id_id"),
        UniqueConstraint(
            "workspace_id",
            "project_id",
            "user_id",
            name="uq_project_members__project_user",
        ),
        Index("ix_project_members__workspace_project", "workspace_id", "project_id"),
        Index("ix_project_members__workspace_user", "workspace_id", "user_id"),
        {"comment": "Project-level user responsibility assignments."},
    )

    project_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    project_role: Mapped[str] = mapped_column(Text, nullable=False)

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="project_members",
        lazy="raise",
        overlaps="members",
    )
    project: Mapped[Project] = relationship(
        "Project", back_populates="members", lazy="raise", overlaps="workspace"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"ProjectMember(id={self.id!r}, project_role={self.project_role!r})"

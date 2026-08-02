"""Campaign/project grouping model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import ProjectStatus
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.project_member import ProjectMember
    from cloud_content_hub.infrastructure.database.models.setting import Setting
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class Project(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable workspace-scoped campaign or project grouping."""

    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint(check_in(ProjectStatus, name="status"), name="ck_projects__status"),
        CheckConstraint(
            "ends_at IS NULL OR starts_at IS NULL OR ends_at > starts_at",
            name="ck_projects__dates",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_projects__workspace_id_id"),
        Index(
            "uq_projects__workspace_slug_where_active",
            "workspace_id",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_projects__workspace_updated_cursor",
            "workspace_id",
            text("updated_at DESC"),
            "id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Campaign/project grouping within a workspace."},
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(CITEXT, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text(f"'{ProjectStatus.ACTIVE.value}'")
    )
    owner_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="projects", lazy="raise"
    )
    members: Mapped[list[ProjectMember]] = relationship(
        "ProjectMember", back_populates="project", lazy="raise"
    )
    content_assets: Mapped[list[ContentAsset]] = relationship(
        "ContentAsset",
        back_populates="project",
        lazy="raise",
        overlaps="content_assets,folder,workspace",
    )

    settings: Mapped[list[Setting]] = relationship(
        "Setting", back_populates="project", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Project(id={self.id!r}, slug={self.slug!r})"

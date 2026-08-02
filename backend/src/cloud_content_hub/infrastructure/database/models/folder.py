"""Content hierarchy folder model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class Folder(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable hierarchical folder for organizing content assets."""

    __tablename__ = "folders"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "parent_folder_id"],
            ["folders.workspace_id", "folders.id"],
            name="fk_folders__parent",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "parent_folder_id IS NULL OR parent_folder_id <> id",
            name="ck_folders__parent_not_self",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_folders__workspace_id_id"),
        Index(
            "ix_folders__workspace_parent_name",
            "workspace_id",
            "parent_folder_id",
            "name",
            postgresql_nulls_not_distinct=True,
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Hierarchical content folder tree within a workspace."},
    )

    parent_folder_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    path_cache: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped[Workspace] = relationship("Workspace", back_populates="folders", lazy="raise")
    parent_folder: Mapped[Folder | None] = relationship(
        "Folder",
        remote_side="Folder.id",
        foreign_keys=[parent_folder_id],
        back_populates="child_folders",
        lazy="raise",
    )
    child_folders: Mapped[list[Folder]] = relationship(
        "Folder",
        back_populates="parent_folder",
        lazy="raise",
        overlaps="workspace",
    )
    content_assets: Mapped[list[ContentAsset]] = relationship(
        "ContentAsset",
        back_populates="folder",
        lazy="raise",
        overlaps="project,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Folder(id={self.id!r}, name={self.name!r})"

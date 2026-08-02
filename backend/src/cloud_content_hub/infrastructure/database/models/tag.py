"""Workspace folksonomy tag model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.asset_tag import AssetTag
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class Tag(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable workspace-scoped folksonomy tag."""

    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("workspace_id", "id", name="uq_tags__workspace_id_id"),
        Index(
            "uq_tags__workspace_name_where_active",
            "workspace_id",
            "name",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Workspace folksonomy tags for content assets."},
    )

    name: Mapped[str] = mapped_column(CITEXT, nullable=False)
    color: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped[Workspace] = relationship("Workspace", back_populates="tags", lazy="raise")
    asset_tags: Mapped[list[AssetTag]] = relationship(
        "AssetTag",
        back_populates="tag",
        lazy="raise",
        overlaps="asset,asset_tags,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Tag(id={self.id!r}, name={self.name!r})"

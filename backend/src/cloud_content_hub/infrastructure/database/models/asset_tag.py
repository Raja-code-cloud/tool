"""Asset and tag bridge junction model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, Index, UniqueConstraint
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
    from cloud_content_hub.infrastructure.database.models.tag import Tag
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class AssetTag(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Junction row linking a content asset to a workspace tag."""

    __tablename__ = "asset_tags"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_asset_tags__asset",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "tag_id"],
            ["tags.workspace_id", "tags.id"],
            name="fk_asset_tags__tag",
            ondelete="RESTRICT",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_asset_tags__workspace_id_id"),
        UniqueConstraint(
            "workspace_id",
            "asset_id",
            "tag_id",
            name="uq_asset_tags__asset_tag",
        ),
        Index("ix_asset_tags__workspace_tag_asset", "workspace_id", "tag_id", "asset_id"),
        Index("ix_asset_tags__workspace_asset_tag", "workspace_id", "asset_id", "tag_id"),
        {"comment": "Many-to-many bridge between content assets and tags."},
    )

    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    tag_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="asset_tags", lazy="raise"
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        back_populates="asset_tags",
        lazy="raise",
        overlaps="workspace",
    )
    tag: Mapped[Tag] = relationship(
        "Tag", back_populates="asset_tags", lazy="raise", overlaps="asset,workspace"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"AssetTag(id={self.id!r}, asset_id={self.asset_id!r}, tag_id={self.tag_id!r})"

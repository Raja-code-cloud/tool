"""Ordered collection membership junction model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Index, Integer, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.collection import Collection
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class CollectionItem(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Junction row linking a content asset to an ordered collection position."""

    __tablename__ = "collection_items"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "collection_id"],
            ["collections.workspace_id", "collections.id"],
            name="fk_collection_items__collection",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_collection_items__asset",
            ondelete="RESTRICT",
        ),
        CheckConstraint("position >= 0", name="ck_collection_items__position"),
        UniqueConstraint("workspace_id", "id", name="uq_collection_items__workspace_id_id"),
        UniqueConstraint(
            "workspace_id",
            "collection_id",
            "asset_id",
            name="uq_collection_items__collection_asset",
        ),
        UniqueConstraint(
            "workspace_id",
            "collection_id",
            "position",
            name="uq_collection_items__collection_position",
        ),
        Index(
            "ix_collection_items__workspace_collection_position",
            "workspace_id",
            "collection_id",
            "position",
            "id",
        ),
        Index(
            "ix_collection_items__workspace_asset",
            "workspace_id",
            "asset_id",
        ),
        {"comment": "Ordered membership of content assets in collections."},
    )

    collection_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="collection_items",
        lazy="raise",
        overlaps="items",
    )
    collection: Mapped[Collection] = relationship(
        "Collection",
        back_populates="items",
        lazy="raise",
        overlaps="workspace",
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        back_populates="collection_items",
        lazy="raise",
        overlaps="collection,items,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"CollectionItem(id={self.id!r}, position={self.position!r})"

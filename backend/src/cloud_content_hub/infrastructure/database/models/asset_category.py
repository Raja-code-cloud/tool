"""Asset and category bridge junction model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKeyConstraint, Index, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.category import Category
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class AssetCategory(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Junction row linking a content asset to a taxonomy category."""

    __tablename__ = "asset_categories"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_asset_categories__asset",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "category_id"],
            ["categories.workspace_id", "categories.id"],
            name="fk_asset_categories__category",
            ondelete="RESTRICT",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_asset_categories__workspace_id_id"),
        UniqueConstraint(
            "workspace_id",
            "asset_id",
            "category_id",
            name="uq_asset_categories__asset_category",
        ),
        Index(
            "uq_asset_categories__one_primary",
            "workspace_id",
            "asset_id",
            unique=True,
            postgresql_where=text("is_primary"),
        ),
        Index(
            "ix_asset_categories__workspace_category_asset",
            "workspace_id",
            "category_id",
            "asset_id",
        ),
        Index(
            "ix_asset_categories__workspace_asset_category",
            "workspace_id",
            "asset_id",
            "category_id",
        ),
        {"comment": "Many-to-many bridge between content assets and categories."},
    )

    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    category_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="asset_categories", lazy="raise"
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        back_populates="asset_categories",
        lazy="raise",
        overlaps="workspace",
    )
    category: Mapped[Category] = relationship(
        "Category",
        back_populates="asset_categories",
        lazy="raise",
        overlaps="asset,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"AssetCategory(id={self.id!r}, is_primary={self.is_primary!r})"

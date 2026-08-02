"""Mutable autosave and editor draft state model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
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
    from cloud_content_hub.infrastructure.database.models.content_version import ContentVersion
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class ContentDraft(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable current autosave and editor state for a content asset."""

    __tablename__ = "content_drafts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_content_drafts__asset",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "base_version_id"],
            ["content_versions.workspace_id", "content_versions.id"],
            name="fk_content_drafts__base_version",
            ondelete="SET NULL",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_content_drafts__workspace_id_id"),
        Index(
            "uq_content_drafts__workspace_asset_where_active",
            "workspace_id",
            "asset_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Current mutable autosave/editor state per content asset."},
    )

    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    base_version_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=True
    )
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_rich: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    autosaved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="content_drafts",
        lazy="raise",
        overlaps="draft",
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset", back_populates="draft", lazy="raise", overlaps="workspace"
    )
    base_version: Mapped[ContentVersion | None] = relationship(
        "ContentVersion",
        back_populates="drafts",
        lazy="raise",
        overlaps="asset,draft,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"ContentDraft(id={self.id!r}, asset_id={self.asset_id!r})"

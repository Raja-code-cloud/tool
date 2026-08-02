"""Poster/image-specific content metadata model."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import UACMixin, WorkspaceMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class Poster(WorkspaceMixin, UACMixin, Base):
    """Mutable poster/image-specific metadata keyed by content asset."""

    __tablename__ = "posters"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_posters__asset",
            ondelete="RESTRICT",
        ),
        CheckConstraint("width IS NULL OR width > 0", name="ck_posters__width"),
        CheckConstraint("height IS NULL OR height > 0", name="ck_posters__height"),
        CheckConstraint(
            "aspect_ratio IS NULL OR aspect_ratio > 0",
            name="ck_posters__aspect_ratio",
        ),
        UniqueConstraint("workspace_id", "asset_id", name="uq_posters__workspace_asset"),
        {"comment": "Poster-specific metadata for content assets of type poster."},
    )

    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    aspect_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    alt_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    crop_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="posters", lazy="raise", overlaps="poster"
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        back_populates="poster",
        lazy="raise",
        overlaps="workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Poster(asset_id={self.asset_id!r})"

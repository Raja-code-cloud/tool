"""Thumbnail-specific content metadata model."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import UACMixin, WorkspaceMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class Thumbnail(WorkspaceMixin, UACMixin, Base):
    """Mutable thumbnail-specific metadata keyed by content asset."""

    __tablename__ = "thumbnails"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_thumbnails__asset",
            ondelete="RESTRICT",
        ),
        CheckConstraint("width IS NULL OR width > 0", name="ck_thumbnails__width"),
        CheckConstraint("height IS NULL OR height > 0", name="ck_thumbnails__height"),
        CheckConstraint(
            "aspect_ratio IS NULL OR aspect_ratio > 0",
            name="ck_thumbnails__aspect_ratio",
        ),
        CheckConstraint(
            "source_time_ms IS NULL OR source_time_ms >= 0",
            name="ck_thumbnails__source_time",
        ),
        UniqueConstraint("workspace_id", "asset_id", name="uq_thumbnails__workspace_asset"),
        {"comment": "Thumbnail-specific metadata for content assets of type thumbnail."},
    )

    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    aspect_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    alt_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_time_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="thumbnails",
        lazy="raise",
        overlaps="thumbnail",
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        back_populates="thumbnail",
        lazy="raise",
        overlaps="workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Thumbnail(asset_id={self.asset_id!r})"

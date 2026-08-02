"""Video-specific content metadata model."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import TranscriptStatus
from cloud_content_hub.infrastructure.database.mixins import UACMixin, WorkspaceMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class Video(WorkspaceMixin, UACMixin, Base):
    """Mutable video-specific metadata keyed by content asset."""

    __tablename__ = "videos"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_videos__asset",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "duration_ms IS NULL OR duration_ms >= 0",
            name="ck_videos__duration",
        ),
        CheckConstraint("width IS NULL OR width > 0", name="ck_videos__width"),
        CheckConstraint("height IS NULL OR height > 0", name="ck_videos__height"),
        CheckConstraint(
            "frame_rate IS NULL OR frame_rate > 0",
            name="ck_videos__frame_rate",
        ),
        CheckConstraint(
            check_in(TranscriptStatus, name="transcript_status"),
            name="ck_videos__transcript_status",
        ),
        UniqueConstraint("workspace_id", "asset_id", name="uq_videos__workspace_asset"),
        Index(
            "ix_videos__workspace_transcript_status",
            "workspace_id",
            "transcript_status",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Video-specific metadata for content assets of type video."},
    )

    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True)
    duration_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frame_rate: Mapped[Decimal | None] = mapped_column(Numeric(8, 3), nullable=True)
    transcript_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text(f"'{TranscriptStatus.NONE.value}'"),
    )
    caption_language: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="videos", lazy="raise", overlaps="video"
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset", back_populates="video", lazy="raise", overlaps="workspace"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Video(asset_id={self.asset_id!r})"

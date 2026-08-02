"""Threaded review comment model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Text,
    UniqueConstraint,
    text,
)
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


class Comment(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable threaded review comment anchored to a content asset."""

    __tablename__ = "comments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_comments__asset",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "version_id"],
            ["content_versions.workspace_id", "content_versions.id"],
            name="fk_comments__version",
            ondelete="SET NULL",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "parent_comment_id"],
            ["comments.workspace_id", "comments.id"],
            name="fk_comments__parent",
            ondelete="RESTRICT",
        ),
        CheckConstraint("length(trim(body)) > 0", name="ck_comments__body_nonblank"),
        UniqueConstraint("workspace_id", "id", name="uq_comments__workspace_id_id"),
        Index(
            "ix_comments__workspace_asset_created_cursor",
            "workspace_id",
            "asset_id",
            text("created_at DESC"),
            "id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_comments__workspace_parent",
            "workspace_id",
            "parent_comment_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Threaded review comments on content assets and versions."},
    )

    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    version_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=True)
    parent_comment_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=True
    )
    author_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    anchor: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="comments", lazy="raise"
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        back_populates="comments",
        lazy="raise",
        overlaps="workspace",
    )
    content_version: Mapped[ContentVersion | None] = relationship(
        "ContentVersion",
        back_populates="comments",
        lazy="raise",
        overlaps="asset,workspace",
    )
    parent_comment: Mapped[Comment | None] = relationship(
        "Comment",
        remote_side="Comment.id",
        foreign_keys=[parent_comment_id],
        back_populates="replies",
        lazy="raise",
    )
    replies: Mapped[list[Comment]] = relationship(
        "Comment",
        back_populates="parent_comment",
        lazy="raise",
        overlaps="asset,content_version,workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Comment(id={self.id!r}, asset_id={self.asset_id!r})"

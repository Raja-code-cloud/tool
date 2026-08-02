"""Article-specific content metadata model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Integer, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import ArticleSourceKind
from cloud_content_hub.infrastructure.database.mixins import UACMixin, WorkspaceMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class Article(WorkspaceMixin, UACMixin, Base):
    """Mutable article-specific metadata keyed by content asset."""

    __tablename__ = "articles"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_articles__asset",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            check_in(ArticleSourceKind, name="source_kind"),
            name="ck_articles__source_kind",
        ),
        CheckConstraint("word_count >= 0", name="ck_articles__word_count"),
        CheckConstraint("reading_minutes >= 0", name="ck_articles__reading_minutes"),
        UniqueConstraint("workspace_id", "asset_id", name="uq_articles__workspace_asset"),
        {"comment": "Article-specific metadata for content assets of type article."},
    )

    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True)
    source_kind: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    language_code: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'en'"))
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    reading_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="articles", lazy="raise"
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        back_populates="article",
        lazy="raise",
        overlaps="workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Article(asset_id={self.asset_id!r})"

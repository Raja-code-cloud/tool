"""Explainable AI editor suggestion model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import AISuggestionCategory, AISuggestionStatus
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.ai_generation_request import (
        AIGenerationRequest,
    )
    from cloud_content_hub.infrastructure.database.models.ai_suggestion_action import (
        AISuggestionAction,
    )
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.content_version import ContentVersion
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class AISuggestion(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable explainable AI or editor recommendation."""

    __tablename__ = "ai_suggestions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_ai_suggestions__asset",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "version_id"],
            ["content_versions.workspace_id", "content_versions.id"],
            name="fk_ai_suggestions__version",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "generation_request_id"],
            ["ai_generation_requests.workspace_id", "ai_generation_requests.id"],
            name="fk_ai_suggestions__generation_request",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "category IN ('grammar','seo','engagement','readability','timing','warning')",
            name="ck_ai_suggestions__category",
        ),
        CheckConstraint(
            "status IN ('open','accepted','dismissed','expired')",
            name="ck_ai_suggestions__status",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_ai_suggestions__workspace_id_id"),
        Index(
            "ix_ai_suggestions__workspace_asset_open",
            "workspace_id",
            "asset_id",
            text("created_at DESC"),
            text("id DESC"),
            postgresql_where=text("deleted_at IS NULL AND status = 'open'"),
        ),
        {"comment": "Explainable AI and editor recommendations for content assets."},
    )

    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    version_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    generation_request_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=True
    )
    category: Mapped[AISuggestionCategory] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_change: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[AISuggestionStatus] = mapped_column(
        Text, nullable=False, server_default=text("'open'")
    )

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="ai_suggestions",
        lazy="raise",
        overlaps="suggestions",
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        back_populates="ai_suggestions",
        lazy="raise",
        overlaps="suggestions,workspace",
    )
    content_version: Mapped[ContentVersion] = relationship(
        "ContentVersion",
        back_populates="ai_suggestions",
        lazy="raise",
        overlaps="asset,suggestions,workspace",
    )
    generation_request: Mapped[AIGenerationRequest | None] = relationship(
        "AIGenerationRequest",
        back_populates="suggestions",
        lazy="raise",
        overlaps="asset,content_version,workspace",
    )
    actions: Mapped[list[AISuggestionAction]] = relationship(
        "AISuggestionAction", back_populates="suggestion", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"AISuggestion(id={self.id!r}, category={self.category!r}, status={self.status!r})"

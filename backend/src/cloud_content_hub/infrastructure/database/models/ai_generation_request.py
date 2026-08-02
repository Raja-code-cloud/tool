"""AI generation request aggregate model."""

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
from cloud_content_hub.infrastructure.database.enums import AIGenerationScope, AIGenerationStatus
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.ai_generation_output import (
        AIGenerationOutput,
    )
    from cloud_content_hub.infrastructure.database.models.ai_model import AIModel
    from cloud_content_hub.infrastructure.database.models.ai_prompt_template import AIPromptTemplate
    from cloud_content_hub.infrastructure.database.models.ai_suggestion import AISuggestion
    from cloud_content_hub.infrastructure.database.models.ai_usage_record import AIUsageRecord
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.content_version import ContentVersion
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class AIGenerationRequest(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable AI generation aggregate and pipeline state."""

    __tablename__ = "ai_generation_requests"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_ai_generation_requests__asset",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "source_version_id"],
            ["content_versions.workspace_id", "content_versions.id"],
            name="fk_ai_generation_requests__source_version",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "prompt_template_id"],
            ["ai_prompt_templates.workspace_id", "ai_prompt_templates.id"],
            name="fk_ai_generation_requests__prompt_template",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "brand_profile_id"],
            ["brand_profiles.workspace_id", "brand_profiles.id"],
            name="fk_ai_generation_requests__brand_profile",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "status IN ('queued','running','succeeded','failed','cancelled')",
            name="ck_ai_generation_requests__status",
        ),
        CheckConstraint(
            "scope IN ('whole','selection','headline','cta','hashtags','tone','platform_variant')",
            name="ck_ai_generation_requests__scope",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_ai_generation_requests__workspace_id_id"),
        Index(
            "uq_ai_generation_requests__workspace_idempotency",
            "workspace_id",
            "idempotency_key",
            unique=True,
        ),
        Index(
            "ix_ai_generation_requests__workspace_due",
            "workspace_id",
            "created_at",
            "id",
            postgresql_where=text("deleted_at IS NULL AND status = 'queued'"),
        ),
        Index(
            "ix_ai_generation_requests__workspace_asset_cursor",
            "workspace_id",
            "asset_id",
            text("created_at DESC"),
            text("id DESC"),
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_ai_generation_requests__provider_request",
            "model_id",
            "provider_request_id",
            postgresql_where=text("provider_request_id IS NOT NULL"),
        ),
        {"comment": "AI generation aggregate with idempotent request tracking."},
    )

    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    source_version_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    model_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("ai_models.id", ondelete="RESTRICT"),
        nullable=False,
    )
    prompt_template_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=True
    )
    brand_profile_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=True
    )
    status: Mapped[AIGenerationStatus] = mapped_column(
        Text, nullable=False, server_default=text("'queued'")
    )
    scope: Mapped[AIGenerationScope] = mapped_column(Text, nullable=False)
    parameters: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    provider_request_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="ai_generation_requests", lazy="raise"
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        back_populates="ai_generation_requests",
        lazy="raise",
        overlaps="workspace",
    )
    source_version: Mapped[ContentVersion] = relationship(
        "ContentVersion",
        back_populates="ai_generation_requests",
        lazy="raise",
        overlaps="asset,workspace",
    )
    model: Mapped[AIModel] = relationship(
        "AIModel", back_populates="generation_requests", lazy="raise"
    )
    prompt_template: Mapped[AIPromptTemplate | None] = relationship(
        "AIPromptTemplate",
        back_populates="generation_requests",
        lazy="raise",
        overlaps="asset,source_version,workspace",
    )
    outputs: Mapped[list[AIGenerationOutput]] = relationship(
        "AIGenerationOutput",
        back_populates="generation_request",
        lazy="raise",
        overlaps="materialized_version,workspace",
    )
    usage_records: Mapped[list[AIUsageRecord]] = relationship(
        "AIUsageRecord", back_populates="generation_request", lazy="raise"
    )
    suggestions: Mapped[list[AISuggestion]] = relationship(
        "AISuggestion", back_populates="generation_request", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"AIGenerationRequest(id={self.id!r}, status={self.status!r})"

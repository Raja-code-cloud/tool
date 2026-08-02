"""Immutable AI generation output candidate model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    LargeBinary,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import AISafetyStatus
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.ai_generation_request import (
        AIGenerationRequest,
    )
    from cloud_content_hub.infrastructure.database.models.content_version import ContentVersion
    from cloud_content_hub.infrastructure.database.models.publication_target import (
        PublicationTarget,
    )
    from cloud_content_hub.infrastructure.database.models.social_platform import SocialPlatform
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class AIGenerationOutput(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Append-only generated candidate output from an AI request."""

    __tablename__ = "ai_generation_outputs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "generation_request_id"],
            ["ai_generation_requests.workspace_id", "ai_generation_requests.id"],
            name="fk_ai_generation_outputs__generation_request",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "materialized_version_id"],
            ["content_versions.workspace_id", "content_versions.id"],
            name="fk_ai_generation_outputs__materialized_version",
            ondelete="RESTRICT",
        ),
        CheckConstraint("sequence_no > 0", name="ck_ai_generation_outputs__sequence_no"),
        CheckConstraint(
            "safety_status IN ('unchecked','passed','flagged','blocked')",
            name="ck_ai_generation_outputs__safety_status",
        ),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="ck_ai_generation_outputs__immutable_uac",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_ai_generation_outputs__workspace_id_id"),
        UniqueConstraint(
            "workspace_id",
            "generation_request_id",
            "sequence_no",
            name="uq_ai_generation_outputs__request_sequence",
        ),
        Index(
            "ix_ai_generation_outputs__workspace_request_sequence",
            "workspace_id",
            "generation_request_id",
            "sequence_no",
        ),
        Index(
            "ix_ai_generation_outputs__materialized_version",
            "workspace_id",
            "materialized_version_id",
            postgresql_where=text("materialized_version_id IS NOT NULL"),
        ),
        Index("ix_ai_generation_outputs__created_at", "created_at", "id"),
        {"comment": "Immutable generated AI output candidates."},
    )

    generation_request_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=False
    )
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    platform_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("social_platforms.id", ondelete="RESTRICT"),
        nullable=True,
    )
    output_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    safety_status: Mapped[AISafetyStatus] = mapped_column(Text, nullable=False)
    content_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    materialized_version_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=True
    )

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="ai_generation_outputs", lazy="raise"
    )
    generation_request: Mapped[AIGenerationRequest] = relationship(
        "AIGenerationRequest",
        back_populates="outputs",
        lazy="raise",
        overlaps="workspace",
    )
    platform: Mapped[SocialPlatform | None] = relationship(
        "SocialPlatform", back_populates="generation_outputs", lazy="raise"
    )
    materialized_version: Mapped[ContentVersion | None] = relationship(
        "ContentVersion",
        back_populates="ai_generation_outputs",
        lazy="raise",
        overlaps="generation_request,workspace",
    )
    publication_targets: Mapped[list[PublicationTarget]] = relationship(
        "PublicationTarget", back_populates="generation_output", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return (
            f"AIGenerationOutput(id={self.id!r}, generation_request_id="
            f"{self.generation_request_id!r}, sequence_no={self.sequence_no!r})"
        )

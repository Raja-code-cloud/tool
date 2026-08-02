"""Immutable content snapshot and provenance model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
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
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import ContentVersionOrigin
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.ai_generation_output import (
        AIGenerationOutput,
    )
    from cloud_content_hub.infrastructure.database.models.ai_generation_request import (
        AIGenerationRequest,
    )
    from cloud_content_hub.infrastructure.database.models.ai_suggestion import AISuggestion
    from cloud_content_hub.infrastructure.database.models.approval_request import ApprovalRequest
    from cloud_content_hub.infrastructure.database.models.comment import Comment
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.content_draft import ContentDraft
    from cloud_content_hub.infrastructure.database.models.publication import Publication
    from cloud_content_hub.infrastructure.database.models.publication_target import (
        PublicationTarget,
    )
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class ContentVersion(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Immutable content snapshot with provenance and deduplication hash."""

    __tablename__ = "content_versions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_content_versions__asset",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "source_version_id"],
            ["content_versions.workspace_id", "content_versions.id"],
            name="fk_content_versions__source_version",
            ondelete="RESTRICT",
        ),
        CheckConstraint("version_number > 0", name="ck_content_versions__version_number"),
        CheckConstraint(
            check_in(ContentVersionOrigin, name="origin"),
            name="ck_content_versions__origin",
        ),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="ck_content_versions__immutable_uac",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_content_versions__workspace_id_id"),
        UniqueConstraint(
            "workspace_id",
            "asset_id",
            "version_number",
            name="uq_content_versions__workspace_asset_number",
        ),
        UniqueConstraint(
            "workspace_id",
            "asset_id",
            "content_hash",
            name="uq_content_versions__workspace_asset_hash",
        ),
        Index(
            "ix_content_versions__workspace_asset_version_desc",
            "workspace_id",
            "asset_id",
            text("version_number DESC"),
            postgresql_include=["created_at", "origin", "content_hash"],
        ),
        {"comment": "Immutable content snapshots retained for publishing and audit."},
    )

    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_rich: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    origin: Mapped[str] = mapped_column(Text, nullable=False)
    source_version_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=True
    )
    content_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="content_versions",
        lazy="raise",
        overlaps="versions",
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        back_populates="versions",
        lazy="raise",
        overlaps="workspace",
    )
    source_version: Mapped[ContentVersion | None] = relationship(
        "ContentVersion",
        remote_side="ContentVersion.id",
        foreign_keys=[source_version_id],
        back_populates="derived_versions",
        lazy="raise",
    )
    derived_versions: Mapped[list[ContentVersion]] = relationship(
        "ContentVersion",
        back_populates="source_version",
        lazy="raise",
        overlaps="asset,versions,workspace",
    )
    drafts: Mapped[list[ContentDraft]] = relationship(
        "ContentDraft",
        back_populates="base_version",
        lazy="raise",
        overlaps="asset,draft,workspace",
    )
    comments: Mapped[list[Comment]] = relationship(
        "Comment",
        back_populates="content_version",
        lazy="raise",
        overlaps="asset,comments,replies,workspace",
    )
    approval_requests: Mapped[list[ApprovalRequest]] = relationship(
        "ApprovalRequest",
        back_populates="content_version",
        lazy="raise",
        overlaps="approval_requests,asset,workspace",
    )

    ai_generation_outputs: Mapped[list[AIGenerationOutput]] = relationship(
        "AIGenerationOutput",
        back_populates="materialized_version",
        lazy="raise",
        overlaps="generation_request,outputs,workspace",
    )
    ai_generation_requests: Mapped[list[AIGenerationRequest]] = relationship(
        "AIGenerationRequest",
        back_populates="source_version",
        lazy="raise",
        overlaps="ai_generation_requests,asset,generation_requests,prompt_template,workspace",
    )
    ai_suggestions: Mapped[list[AISuggestion]] = relationship(
        "AISuggestion",
        back_populates="content_version",
        lazy="raise",
        overlaps="ai_suggestions,asset,generation_request,suggestions,workspace",
    )
    publication_targets: Mapped[list[PublicationTarget]] = relationship(
        "PublicationTarget",
        back_populates="content_version",
        lazy="raise",
        overlaps="publication_targets",
    )
    publications: Mapped[list[Publication]] = relationship(
        "Publication",
        back_populates="content_version",
        lazy="raise",
        overlaps="publications",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"ContentVersion(id={self.id!r}, version_number={self.version_number!r})"

"""Master content aggregate and library record model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import AssetType, ContentLifecycle
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.ai_generation_request import (
        AIGenerationRequest,
    )
    from cloud_content_hub.infrastructure.database.models.ai_suggestion import AISuggestion
    from cloud_content_hub.infrastructure.database.models.approval_request import ApprovalRequest
    from cloud_content_hub.infrastructure.database.models.article import Article
    from cloud_content_hub.infrastructure.database.models.asset_category import AssetCategory
    from cloud_content_hub.infrastructure.database.models.asset_storage_object import (
        AssetStorageObject,
    )
    from cloud_content_hub.infrastructure.database.models.asset_tag import AssetTag
    from cloud_content_hub.infrastructure.database.models.collection_item import CollectionItem
    from cloud_content_hub.infrastructure.database.models.comment import Comment
    from cloud_content_hub.infrastructure.database.models.content_draft import ContentDraft
    from cloud_content_hub.infrastructure.database.models.content_performance_snapshot import (
        ContentPerformanceSnapshot,
    )
    from cloud_content_hub.infrastructure.database.models.content_relation import ContentRelation
    from cloud_content_hub.infrastructure.database.models.content_version import ContentVersion
    from cloud_content_hub.infrastructure.database.models.folder import Folder
    from cloud_content_hub.infrastructure.database.models.metric_observation import (
        MetricObservation,
    )
    from cloud_content_hub.infrastructure.database.models.poster import Poster
    from cloud_content_hub.infrastructure.database.models.project import Project
    from cloud_content_hub.infrastructure.database.models.publication import Publication
    from cloud_content_hub.infrastructure.database.models.thumbnail import Thumbnail
    from cloud_content_hub.infrastructure.database.models.video import Video
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class ContentAsset(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable master content library row and aggregate root."""

    __tablename__ = "content_assets"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "project_id"],
            ["projects.workspace_id", "projects.id"],
            name="fk_content_assets__project",
            ondelete="SET NULL",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "folder_id"],
            ["folders.workspace_id", "folders.id"],
            name="fk_content_assets__folder",
            ondelete="SET NULL",
        ),
        CheckConstraint(
            check_in(AssetType, name="asset_type"), name="ck_content_assets__asset_type"
        ),
        CheckConstraint(
            check_in(ContentLifecycle, name="lifecycle_status"),
            name="ck_content_assets__lifecycle_status",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_content_assets__workspace_id_id"),
        Index(
            "ix_content_assets__workspace_updated_cursor",
            "workspace_id",
            text("updated_at DESC"),
            "id",
            postgresql_include=["title", "asset_type", "lifecycle_status", "owner_id"],
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_content_assets__workspace_type_status_updated",
            "workspace_id",
            "asset_type",
            "lifecycle_status",
            text("updated_at DESC"),
            "id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_content_assets__workspace_owner_updated",
            "workspace_id",
            "owner_id",
            text("updated_at DESC"),
            "id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_content_assets__workspace_project_updated",
            "workspace_id",
            "project_id",
            text("updated_at DESC"),
            "id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_content_assets__workspace_folder_updated",
            "workspace_id",
            "folder_id",
            text("updated_at DESC"),
            "id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_content_assets__search_gin",
            "search_document",
            postgresql_using="gin",
        ),
        {"comment": "Master content aggregate and library record."},
    )

    project_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=True)
    folder_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=True)
    asset_type: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    lifecycle_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text(f"'{ContentLifecycle.DRAFT.value}'"),
    )
    owner_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    search_document: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="content_assets", lazy="raise"
    )
    project: Mapped[Project | None] = relationship(
        "Project",
        back_populates="content_assets",
        lazy="raise",
        overlaps="workspace",
    )
    folder: Mapped[Folder | None] = relationship(
        "Folder",
        back_populates="content_assets",
        lazy="raise",
        overlaps="project,workspace",
    )
    article: Mapped[Article | None] = relationship(
        "Article",
        back_populates="asset",
        uselist=False,
        lazy="raise",
        overlaps="workspace",
    )
    video: Mapped[Video | None] = relationship(
        "Video", back_populates="asset", uselist=False, lazy="raise"
    )
    poster: Mapped[Poster | None] = relationship(
        "Poster", back_populates="asset", uselist=False, lazy="raise"
    )
    thumbnail: Mapped[Thumbnail | None] = relationship(
        "Thumbnail", back_populates="asset", uselist=False, lazy="raise"
    )
    collection_items: Mapped[list[CollectionItem]] = relationship(
        "CollectionItem",
        back_populates="asset",
        lazy="raise",
        overlaps="collection,items,workspace",
    )
    asset_tags: Mapped[list[AssetTag]] = relationship(
        "AssetTag",
        back_populates="asset",
        lazy="raise",
        overlaps="tag,workspace",
    )
    asset_categories: Mapped[list[AssetCategory]] = relationship(
        "AssetCategory",
        back_populates="asset",
        lazy="raise",
        overlaps="asset_categories,category,workspace",
    )
    asset_storage_objects: Mapped[list[AssetStorageObject]] = relationship(
        "AssetStorageObject",
        back_populates="asset",
        lazy="raise",
        overlaps="storage_object,workspace",
    )
    draft: Mapped[ContentDraft | None] = relationship(
        "ContentDraft", back_populates="asset", uselist=False, lazy="raise"
    )
    versions: Mapped[list[ContentVersion]] = relationship(
        "ContentVersion", back_populates="asset", lazy="raise"
    )
    comments: Mapped[list[Comment]] = relationship(
        "Comment",
        back_populates="asset",
        lazy="raise",
        overlaps="content_version,replies,workspace",
    )
    approval_requests: Mapped[list[ApprovalRequest]] = relationship(
        "ApprovalRequest",
        back_populates="asset",
        lazy="raise",
        overlaps="content_version,workspace",
    )
    outgoing_relations: Mapped[list[ContentRelation]] = relationship(
        "ContentRelation",
        foreign_keys="ContentRelation.source_asset_id",
        back_populates="source_asset",
        lazy="raise",
    )
    incoming_relations: Mapped[list[ContentRelation]] = relationship(
        "ContentRelation",
        foreign_keys="ContentRelation.target_asset_id",
        back_populates="target_asset",
        lazy="raise",
    )
    metric_observations: Mapped[list[MetricObservation]] = relationship(
        "MetricObservation", back_populates="content_asset", lazy="raise"
    )
    performance_snapshots: Mapped[list[ContentPerformanceSnapshot]] = relationship(
        "ContentPerformanceSnapshot", back_populates="content_asset", lazy="raise"
    )

    ai_generation_requests: Mapped[list[AIGenerationRequest]] = relationship(
        "AIGenerationRequest",
        back_populates="asset",
        lazy="raise",
        overlaps="generation_requests,prompt_template,source_version,workspace",
    )
    ai_suggestions: Mapped[list[AISuggestion]] = relationship(
        "AISuggestion",
        back_populates="asset",
        lazy="raise",
        overlaps="content_version,generation_request,suggestions,workspace",
    )
    publications: Mapped[list[Publication]] = relationship(
        "Publication", back_populates="asset", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"ContentAsset(id={self.id!r}, title={self.title!r})"

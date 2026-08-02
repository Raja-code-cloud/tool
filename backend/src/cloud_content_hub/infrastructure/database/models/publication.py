"""Publication aggregate for approved content model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import PublicationStatus
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.content_version import ContentVersion
    from cloud_content_hub.infrastructure.database.models.publication_target import (
        PublicationTarget,
    )
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class Publication(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable publish aggregate binding approved content to targets."""

    __tablename__ = "publications"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_publications__asset",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "version_id"],
            ["content_versions.workspace_id", "content_versions.id"],
            name="fk_publications__version",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "approval_request_id"],
            ["approval_requests.workspace_id", "approval_requests.id"],
            name="fk_publications__approval_request",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "status IN ('draft','ready','in_progress','completed','partially_failed','cancelled')",
            name="ck_publications__status",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_publications__workspace_id_id"),
        Index(
            "ix_publications__workspace_asset_cursor",
            "workspace_id",
            "asset_id",
            text("updated_at DESC"),
            text("id DESC"),
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "uq_publications__workspace_version_where_active",
            "workspace_id",
            "version_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND status <> 'cancelled'"),
        ),
        {"comment": "Publish aggregate for approved content versions."},
    )

    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    version_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    approval_request_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=True
    )
    status: Mapped[PublicationStatus] = mapped_column(
        Text, nullable=False, server_default=text("'draft'")
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="publications",
        lazy="raise",
        overlaps="publications,publications",
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        back_populates="publications",
        lazy="raise",
        overlaps="publications,workspace",
    )
    content_version: Mapped[ContentVersion] = relationship(
        "ContentVersion",
        back_populates="publications",
        lazy="raise",
        overlaps="asset,publications,workspace",
    )
    targets: Mapped[list[PublicationTarget]] = relationship(
        "PublicationTarget",
        back_populates="publication",
        lazy="raise",
        overlaps="publication_targets,publication_targets",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Publication(id={self.id!r}, status={self.status!r}, title={self.title!r})"

"""Approval workflow request model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
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
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import ApprovalState
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.approval_step import ApprovalStep
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.content_version import ContentVersion
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class ApprovalRequest(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable approval workflow instance for a content version."""

    __tablename__ = "approval_requests"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "asset_id"],
            ["content_assets.workspace_id", "content_assets.id"],
            name="fk_approval_requests__asset",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "version_id"],
            ["content_versions.workspace_id", "content_versions.id"],
            name="fk_approval_requests__version",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            check_in(ApprovalState, name="status"),
            name="ck_approval_requests__status",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_approval_requests__workspace_id_id"),
        Index(
            "uq_approval_requests__one_pending_per_version",
            "workspace_id",
            "version_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND status = 'pending'"),
        ),
        Index(
            "ix_approval_requests__workspace_pending",
            "workspace_id",
            text("requested_at"),
            "id",
            postgresql_where=text("deleted_at IS NULL AND status = 'pending'"),
        ),
        {"comment": "Approval workflow instance for a specific content version."},
    )

    asset_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    version_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text(f"'{ApprovalState.PENDING.value}'"),
    )
    requested_by: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="approval_requests", lazy="raise"
    )
    asset: Mapped[ContentAsset] = relationship(
        "ContentAsset",
        back_populates="approval_requests",
        lazy="raise",
        overlaps="workspace",
    )
    content_version: Mapped[ContentVersion] = relationship(
        "ContentVersion",
        back_populates="approval_requests",
        lazy="raise",
        overlaps="asset,workspace",
    )
    steps: Mapped[list[ApprovalStep]] = relationship(
        "ApprovalStep", back_populates="approval_request", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"ApprovalRequest(id={self.id!r}, status={self.status!r})"

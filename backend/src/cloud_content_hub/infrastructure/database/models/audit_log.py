"""Append-only security and material-change audit model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, LargeBinary, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import AuditActorType, AuditOutcome
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.organization import Organization
    from cloud_content_hub.infrastructure.database.models.user import User
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class AuditLog(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Immutable, redacted evidence for security and material state changes."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        CheckConstraint(
            "actor_type IN ('user','service','system','provider')",
            name="audit_logs_actor_type",
        ),
        CheckConstraint(
            "outcome IN ('success','failure','denied')",
            name="audit_logs_outcome",
        ),
        CheckConstraint(
            "workspace_id IS NOT NULL OR organization_id IS NOT NULL OR source = 'global'",
            name="audit_logs_scope",
        ),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="audit_logs_immutable_shape",
        ),
        Index(
            "ix_audit_logs__workspace_time",
            "workspace_id",
            text("occurred_at DESC"),
            text("id DESC"),
        ),
        Index(
            "ix_audit_logs__organization_time",
            "organization_id",
            text("occurred_at DESC"),
            text("id DESC"),
        ),
        Index(
            "brin_audit_logs__occurred_at",
            "occurred_at",
            postgresql_using="brin",
            postgresql_with={"pages_per_range": 64},
        ),
        {"comment": "Append-only redacted security and compliance evidence."},
    )

    workspace_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=True,
    )
    organization_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=True,
    )
    actor_user_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    actor_type: Mapped[AuditActorType] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    target_type: Mapped[str] = mapped_column(Text, nullable=False)
    target_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=True)
    outcome: Mapped[AuditOutcome] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=True)
    request_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    safe_diff: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    ip_hash: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    workspace: Mapped[Workspace | None] = relationship(
        "Workspace", back_populates="audit_logs", lazy="raise"
    )
    organization: Mapped[Organization | None] = relationship(
        "Organization", back_populates="audit_logs", lazy="raise"
    )
    actor_user: Mapped[User | None] = relationship(
        "User", foreign_keys=[actor_user_id], back_populates="audit_logs", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"AuditLog(id={self.id!r}, action={self.action!r}, outcome={self.outcome!r})"

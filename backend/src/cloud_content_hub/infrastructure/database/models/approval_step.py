"""Ordered reviewer approval step model."""

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
    Integer,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import ApprovalStepState
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.approval_request import ApprovalRequest
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class ApprovalStep(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable ordered reviewer decision within an approval request."""

    __tablename__ = "approval_steps"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "approval_request_id"],
            ["approval_requests.workspace_id", "approval_requests.id"],
            name="fk_approval_steps__approval_request",
            ondelete="RESTRICT",
        ),
        CheckConstraint("step_order > 0", name="ck_approval_steps__step_order"),
        CheckConstraint(
            check_in(ApprovalStepState, name="status"),
            name="ck_approval_steps__status",
        ),
        CheckConstraint(
            "(reviewer_user_id IS NOT NULL AND reviewer_role_id IS NULL) OR "
            "(reviewer_user_id IS NULL AND reviewer_role_id IS NOT NULL)",
            name="ck_approval_steps__reviewer_selector",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_approval_steps__workspace_id_id"),
        Index(
            "uq_approval_steps__request_step_where_active",
            "workspace_id",
            "approval_request_id",
            "step_order",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_approval_steps__workspace_reviewer_pending",
            "workspace_id",
            "reviewer_user_id",
            "created_at",
            "id",
            postgresql_where=text("deleted_at IS NULL AND status = 'pending'"),
        ),
        {"comment": "Ordered reviewer decisions within an approval request."},
    )

    approval_request_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    reviewer_user_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewer_role_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text(f"'{ApprovalStepState.PENDING.value}'"),
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="approval_steps",
        lazy="raise",
        overlaps="steps",
    )
    approval_request: Mapped[ApprovalRequest] = relationship(
        "ApprovalRequest",
        back_populates="steps",
        lazy="raise",
        overlaps="workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"ApprovalStep(id={self.id!r}, step_order={self.step_order!r})"

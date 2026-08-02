"""Immutable AI suggestion decision history model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import (
    AISuggestionAction as AISuggestionActionKind,
)
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.ai_suggestion import AISuggestion
    from cloud_content_hub.infrastructure.database.models.user import User
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class AISuggestionAction(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Append-only suggestion decision history."""

    __tablename__ = "ai_suggestion_actions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "suggestion_id"],
            ["ai_suggestions.workspace_id", "ai_suggestions.id"],
            name="fk_ai_suggestion_actions__suggestion",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "action IN ('accepted','dismissed','reopened','applied')",
            name="ck_ai_suggestion_actions__action",
        ),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="ck_ai_suggestion_actions__immutable_uac",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_ai_suggestion_actions__workspace_id_id"),
        Index(
            "ix_ai_suggestion_actions__workspace_suggestion_created",
            "workspace_id",
            "suggestion_id",
            "created_at",
            "id",
        ),
        Index("ix_ai_suggestion_actions__created_at", "created_at", "id"),
        {"comment": "Immutable AI suggestion decision audit trail."},
    )

    suggestion_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    action: Mapped[AISuggestionActionKind] = mapped_column(Text, nullable=False)
    actor_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="ai_suggestion_actions",
        lazy="raise",
        overlaps="actions",
    )
    suggestion: Mapped[AISuggestion] = relationship(
        "AISuggestion",
        back_populates="actions",
        lazy="raise",
        overlaps="workspace",
    )
    actor: Mapped[User | None] = relationship("User", foreign_keys=[actor_id], lazy="raise")

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"AISuggestionAction(id={self.id!r}, action={self.action!r})"

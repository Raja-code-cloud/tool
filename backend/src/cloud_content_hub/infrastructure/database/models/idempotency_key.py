"""Workspace request idempotency model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, LargeBinary, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class IdempotencyKey(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Short-lived request fingerprint and replay result."""

    __tablename__ = "idempotency_keys"
    __table_args__ = (
        CheckConstraint(
            "state IN ('processing','completed','failed')",
            name="idempotency_keys_state",
        ),
        Index(
            "uq_idempotency_keys__scope_principal_operation_key_where_active",
            "workspace_id",
            "principal_id",
            "operation",
            "key",
            unique=True,
            postgresql_nulls_not_distinct=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_idempotency_keys__expiry", "expires_at", "id"),
        {"comment": "Short-lived request deduplication and response replay state."},
    )

    principal_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=True)
    key: Mapped[str] = mapped_column(Text, nullable=False)
    operation: Mapped[str] = mapped_column(Text, nullable=False)
    request_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    state: Mapped[str] = mapped_column(Text, nullable=False)
    response_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_headers: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    response_body_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    locked_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="idempotency_keys", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe representation that does not expose the key."""

        return f"IdempotencyKey(id={self.id!r}, operation={self.operation!r})"

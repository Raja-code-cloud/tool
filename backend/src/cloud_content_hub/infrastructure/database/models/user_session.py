"""Revocable session and refresh metadata model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, LargeBinary, Text, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.user import User


class UserSession(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Append-only session revocation metadata; never stores bearer tokens."""

    __tablename__ = "user_sessions"
    __table_args__ = (
        CheckConstraint("expires_at > issued_at", name="ck_user_sessions__expires_after_issued"),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="ck_user_sessions__immutable_uac",
        ),
        Index(
            "uq_user_sessions__session_hash",
            "session_hash",
            unique=True,
        ),
        Index(
            "ix_user_sessions__user_expires",
            "user_id",
            text("expires_at DESC"),
        ),
        {"comment": "Revocable session metadata with hashed identifiers only."},
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    session_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    provider_session_id_hash: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revocation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_hash: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    user_agent_hash: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    user: Mapped[User] = relationship(
        "User", foreign_keys=[user_id], back_populates="user_sessions", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"UserSession(id={self.id!r}, user_id={self.user_id!r})"

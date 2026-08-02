"""OIDC external subject mapping model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, LargeBinary, Text, text
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.user import User


class ExternalIdentity(UUIDPrimaryKeyMixin, UACMixin, Base):
    """OIDC issuer/subject mapping without token or claims payload storage."""

    __tablename__ = "external_identities"
    __table_args__ = (
        Index(
            "uq_external_identities__issuer_subject",
            "issuer",
            "subject",
            unique=True,
        ),
        Index(
            "uq_external_identities__user_issuer_where_active",
            "user_id",
            "issuer",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "OIDC subject mapping only; no bearer tokens or raw claims."},
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    issuer: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    provider_code: Mapped[str] = mapped_column(Text, nullable=False)
    email_at_link: Mapped[str | None] = mapped_column(CITEXT, nullable=True)
    claims_fingerprint: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    linked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    user: Mapped[User] = relationship(
        "User", foreign_keys=[user_id], back_populates="external_identities", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"ExternalIdentity(id={self.id!r}, provider_code={self.provider_code!r})"

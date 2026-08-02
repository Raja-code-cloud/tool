"""Encrypted OAuth token vault model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    LargeBinary,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import OAuthTokenStatus
from cloud_content_hub.infrastructure.database.mixins import (
    UACMixin,
    UUIDPrimaryKeyMixin,
    WorkspaceMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.social_account import SocialAccount
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class OAuthTokenVault(UUIDPrimaryKeyMixin, WorkspaceMixin, UACMixin, Base):
    """Mutable encrypted OAuth secret metadata for a social account."""

    __tablename__ = "oauth_token_vaults"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "social_account_id"],
            ["social_accounts.workspace_id", "social_accounts.id"],
            name="fk_oauth_token_vaults__social_account",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "status IN ('active','expiring_soon','expired','renew_required','revoked')",
            name="ck_oauth_token_vaults__status",
        ),
        CheckConstraint(
            "(ciphertext IS NOT NULL AND managed_secret_ref IS NULL) OR "
            "(ciphertext IS NULL AND managed_secret_ref IS NOT NULL)",
            name="ck_oauth_token_vaults__secret_source",
        ),
        UniqueConstraint("workspace_id", "id", name="uq_oauth_token_vaults__workspace_id_id"),
        Index(
            "uq_oauth_token_vaults__workspace_account_where_active",
            "workspace_id",
            "social_account_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_oauth_token_vaults__expiry_due",
            "expires_at",
            "social_account_id",
            postgresql_where=text("deleted_at IS NULL AND status IN ('active','expiring_soon')"),
        ),
        Index(
            "ix_oauth_token_vaults__workspace_account",
            "workspace_id",
            "social_account_id",
        ),
        {"comment": "Encrypted OAuth token metadata; no plaintext secrets stored."},
    )

    social_account_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    ciphertext: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    managed_secret_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_id: Mapped[str] = mapped_column(Text, nullable=False)
    key_version: Mapped[str] = mapped_column(Text, nullable=False)
    token_fingerprint: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    scopes_hash: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[OAuthTokenStatus] = mapped_column(Text, nullable=False)

    workspace: Mapped[Workspace] = relationship(
        "Workspace", back_populates="oauth_token_vaults", lazy="raise"
    )
    social_account: Mapped[SocialAccount] = relationship(
        "SocialAccount",
        back_populates="oauth_token_vaults",
        lazy="raise",
        overlaps="workspace",
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"OAuthTokenVault(id={self.id!r}, status={self.status!r})"

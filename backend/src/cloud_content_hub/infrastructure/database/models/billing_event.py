"""Immutable billing webhook and accounting evidence model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    LargeBinary,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    OrganizationMixin,
    UACMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.organization import Organization


class BillingEvent(UUIDPrimaryKeyMixin, OrganizationMixin, UACMixin, Base):
    """Append-only redacted billing provider event evidence."""

    __tablename__ = "billing_events"
    __table_args__ = (
        CheckConstraint(
            "amount IS NULL OR amount >= 0",
            name="ck_billing_events__amount",
        ),
        CheckConstraint(
            "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
            "AND deleted_at IS NULL AND version = 1",
            name="ck_billing_events__immutable_uac",
        ),
        UniqueConstraint("organization_id", "id", name="uq_billing_events__organization_id_id"),
        Index(
            "uq_billing_events__provider_event",
            "provider_code",
            "external_event_id",
            unique=True,
        ),
        Index(
            "ix_billing_events__organization_time",
            "organization_id",
            text("occurred_at DESC"),
            text("id DESC"),
        ),
        {"comment": "Immutable redacted billing webhook and accounting evidence."},
    )

    provider_code: Mapped[str] = mapped_column(Text, nullable=False)
    external_event_id: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    payload_fragment: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    payload_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="billing_events", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"BillingEvent(id={self.id!r}, event_type={self.event_type!r})"

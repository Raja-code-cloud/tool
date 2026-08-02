"""External subscription mirror model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Index, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import SubscriptionStatus
from cloud_content_hub.infrastructure.database.mixins import (
    OrganizationMixin,
    UACMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.organization import Organization
    from cloud_content_hub.infrastructure.database.models.subscription_item import SubscriptionItem


class Subscription(UUIDPrimaryKeyMixin, OrganizationMixin, UACMixin, Base):
    """Mutable mirror of an external billing provider subscription."""

    __tablename__ = "subscriptions"
    __table_args__ = (
        CheckConstraint(
            check_in(SubscriptionStatus, name="status"),
            name="ck_subscriptions__status",
        ),
        CheckConstraint(
            "current_period_end IS NULL OR current_period_start IS NULL "
            "OR current_period_end > current_period_start",
            name="ck_subscriptions__current_period",
        ),
        UniqueConstraint("organization_id", "id", name="uq_subscriptions__organization_id_id"),
        Index(
            "uq_subscriptions__provider_external",
            "provider_code",
            "external_subscription_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "uq_subscriptions__one_current_org",
            "organization_id",
            unique=True,
            postgresql_where=text(
                "deleted_at IS NULL AND status IN ('trialing','active','past_due','paused')"
            ),
        ),
        {"comment": "External subscription mirror; the provider remains billing authority."},
    )

    provider_code: Mapped[str] = mapped_column(Text, nullable=False)
    external_subscription_id: Mapped[str] = mapped_column(Text, nullable=False)
    plan_code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancel_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="subscriptions", lazy="raise"
    )
    items: Mapped[list[SubscriptionItem]] = relationship(
        "SubscriptionItem", back_populates="subscription", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Subscription(id={self.id!r}, status={self.status!r})"

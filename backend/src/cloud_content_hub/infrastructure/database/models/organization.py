"""Commercial organization boundary model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index, Text, text
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import OrganizationStatus
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.audit_log import AuditLog
    from cloud_content_hub.infrastructure.database.models.billing_customer import BillingCustomer
    from cloud_content_hub.infrastructure.database.models.billing_event import BillingEvent
    from cloud_content_hub.infrastructure.database.models.organization_membership import (
        OrganizationMembership,
    )
    from cloud_content_hub.infrastructure.database.models.outbox_event import OutboxEvent
    from cloud_content_hub.infrastructure.database.models.quota_period import QuotaPeriod
    from cloud_content_hub.infrastructure.database.models.quota_policy import QuotaPolicy
    from cloud_content_hub.infrastructure.database.models.setting import Setting
    from cloud_content_hub.infrastructure.database.models.subscription import Subscription
    from cloud_content_hub.infrastructure.database.models.subscription_item import SubscriptionItem
    from cloud_content_hub.infrastructure.database.models.usage_event import UsageEvent
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace


class Organization(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Global commercial customer boundary and billing root."""

    __tablename__ = "organizations"
    __table_args__ = (
        CheckConstraint(
            check_in(OrganizationStatus, name="status"), name="ck_organizations__status"
        ),
        Index(
            "uq_organizations__slug_where_active",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Commercial customer boundary; legal and billing hold aware."},
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(CITEXT, nullable=False)
    status: Mapped[OrganizationStatus] = mapped_column(
        Text, nullable=False, server_default=text("'active'")
    )
    billing_email: Mapped[str | None] = mapped_column(CITEXT, nullable=True)
    default_time_zone: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'UTC'")
    )
    data_region: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspaces: Mapped[list[Workspace]] = relationship(
        "Workspace", back_populates="organization", lazy="raise"
    )
    organization_memberships: Mapped[list[OrganizationMembership]] = relationship(
        "OrganizationMembership", back_populates="organization", lazy="raise"
    )
    subscriptions: Mapped[list[Subscription]] = relationship(
        "Subscription", back_populates="organization", lazy="raise"
    )
    quota_policies: Mapped[list[QuotaPolicy]] = relationship(
        "QuotaPolicy", back_populates="organization", lazy="raise"
    )
    quota_periods: Mapped[list[QuotaPeriod]] = relationship(
        "QuotaPeriod", back_populates="organization", lazy="raise"
    )
    usage_events: Mapped[list[UsageEvent]] = relationship(
        "UsageEvent", back_populates="organization", lazy="raise"
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(
        "AuditLog", back_populates="organization", lazy="raise"
    )
    outbox_events: Mapped[list[OutboxEvent]] = relationship(
        "OutboxEvent", back_populates="organization", lazy="raise"
    )
    billing_customers: Mapped[list[BillingCustomer]] = relationship(
        "BillingCustomer", back_populates="organization", lazy="raise"
    )
    billing_events: Mapped[list[BillingEvent]] = relationship(
        "BillingEvent", back_populates="organization", lazy="raise"
    )

    settings: Mapped[list[Setting]] = relationship(
        "Setting", back_populates="organization", lazy="raise"
    )
    subscription_items: Mapped[list[SubscriptionItem]] = relationship(
        "SubscriptionItem", back_populates="organization", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Organization(id={self.id!r}, slug={self.slug!r}, status={self.status!r})"

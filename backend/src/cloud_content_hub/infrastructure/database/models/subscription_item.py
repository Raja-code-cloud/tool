"""Subscription meter, seat, or feature line item model."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import (
    OrganizationMixin,
    UACMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.organization import Organization
    from cloud_content_hub.infrastructure.database.models.subscription import Subscription
    from cloud_content_hub.infrastructure.database.models.usage_dimension import UsageDimension


class SubscriptionItem(UUIDPrimaryKeyMixin, OrganizationMixin, UACMixin, Base):
    """Mutable mirror of a subscription meter, seat, or feature line item."""

    __tablename__ = "subscription_items"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_subscription_items__quantity"),
        CheckConstraint(
            "unit_amount IS NULL OR unit_amount >= 0",
            name="ck_subscription_items__unit_amount",
        ),
        UniqueConstraint("organization_id", "id", name="uq_subscription_items__organization_id_id"),
        Index(
            "uq_subscription_items__subscription_price_dimension_where_active",
            "subscription_id",
            "price_code",
            "usage_dimension_id",
            unique=True,
            postgresql_nulls_not_distinct=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_subscription_items__organization_subscription",
            "organization_id",
            "subscription_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "External subscription line items mirrored for metering and entitlements."},
    )

    subscription_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    usage_dimension_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("usage_dimensions.id", ondelete="RESTRICT"),
        nullable=True,
    )
    external_item_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_code: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    unit_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="subscription_items", lazy="raise"
    )
    subscription: Mapped[Subscription] = relationship(
        "Subscription", back_populates="items", lazy="raise"
    )
    usage_dimension: Mapped[UsageDimension | None] = relationship(
        "UsageDimension", back_populates="subscription_items", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"SubscriptionItem(id={self.id!r}, price_code={self.price_code!r})"

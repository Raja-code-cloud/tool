"""Extensible metered-resource catalog model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.quota_period import QuotaPeriod
    from cloud_content_hub.infrastructure.database.models.quota_policy import QuotaPolicy
    from cloud_content_hub.infrastructure.database.models.subscription_item import SubscriptionItem
    from cloud_content_hub.infrastructure.database.models.usage_event import UsageEvent


class UsageDimension(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Global catalog entry describing a metered resource."""

    __tablename__ = "usage_dimensions"
    __table_args__ = (
        CheckConstraint(
            "aggregation IN ('sum','max','last')", name="ck_usage_dimensions__aggregation"
        ),
        UniqueConstraint("code", name="uq_usage_dimensions__code"),
        {"comment": "Extensible catalog of metered resources and aggregation semantics."},
    )

    code: Mapped[str] = mapped_column(CITEXT, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str] = mapped_column(Text, nullable=False)
    aggregation: Mapped[str] = mapped_column(Text, nullable=False)
    billable: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    events: Mapped[list[UsageEvent]] = relationship(
        "UsageEvent", back_populates="usage_dimension", lazy="raise"
    )
    quota_policies: Mapped[list[QuotaPolicy]] = relationship(
        "QuotaPolicy", back_populates="usage_dimension", lazy="raise"
    )
    quota_periods: Mapped[list[QuotaPeriod]] = relationship(
        "QuotaPeriod", back_populates="usage_dimension", lazy="raise"
    )
    subscription_items: Mapped[list[SubscriptionItem]] = relationship(
        "SubscriptionItem", back_populates="usage_dimension", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"UsageDimension(id={self.id!r}, code={self.code!r})"

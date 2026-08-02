"""AI model catalog ORM model."""

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin


class AIModel(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Provider-specific, globally available AI model catalog entry."""

    __tablename__ = "ai_models"
    __table_args__ = (
        CheckConstraint("context_window IS NULL OR context_window > 0", name="context_window"),
        CheckConstraint(
            "input_cost_per_million IS NULL OR input_cost_per_million >= 0",
            name="input_cost_nonnegative",
        ),
        CheckConstraint(
            "output_cost_per_million IS NULL OR output_cost_per_million >= 0",
            name="output_cost_nonnegative",
        ),
        CheckConstraint("status IN ('enabled', 'disabled', 'deprecated')", name="status_values"),
        Index("uq_ai_models__provider_model_code", "provider_id", "model_code", unique=True),
        Index("ix_ai_models__provider_status", "provider_id", "status"),
        {"comment": "Provider-specific global AI model catalog."},
    )

    provider_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("ai_providers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    model_code: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    capabilities: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    context_window: Mapped[int | None] = mapped_column(Integer)
    input_cost_per_million: Mapped[Decimal | None] = mapped_column(Numeric(20, 8))
    output_cost_per_million: Mapped[Decimal | None] = mapped_column(Numeric(20, 8))
    currency: Mapped[str | None] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(Text, nullable=False)

    provider: Mapped[Any] = relationship("AIProvider", back_populates="models", lazy="joined")
    generation_requests: Mapped[list[Any]] = relationship(
        "AIGenerationRequest", back_populates="model", lazy="selectin"
    )
    usage_records: Mapped[list[Any]] = relationship(
        "AIUsageRecord", back_populates="model", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"AIModel(id={self.id!r}, model_code={self.model_code!r})"

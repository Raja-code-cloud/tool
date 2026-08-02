"""Extensible social publishing platform catalog model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, Index, Text, text
from sqlalchemy.dialects.postgresql import CITEXT, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import PlatformStatus
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.ai_generation_output import (
        AIGenerationOutput,
    )
    from cloud_content_hub.infrastructure.database.models.metric_definition import MetricDefinition
    from cloud_content_hub.infrastructure.database.models.publication_target import (
        PublicationTarget,
    )
    from cloud_content_hub.infrastructure.database.models.social_account import SocialAccount
    from cloud_content_hub.infrastructure.database.models.social_content_template import (
        SocialContentTemplate,
    )
    from cloud_content_hub.infrastructure.database.models.social_platform_capability import (
        SocialPlatformCapability,
    )


class SocialPlatform(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Global extensible publishing platform catalog entry."""

    __tablename__ = "social_platforms"
    __table_args__ = (
        CheckConstraint(
            "status IN ('enabled','disabled','coming_soon')",
            name="ck_social_platforms__status",
        ),
        Index("uq_social_platforms__code", "code", unique=True),
        {"comment": "Extensible global social publishing platform catalog."},
    )

    code: Mapped[str] = mapped_column(CITEXT(), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PlatformStatus] = mapped_column(Text, nullable=False)
    api_version: Mapped[str | None] = mapped_column(Text, nullable=True)
    capability_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )

    metric_definitions: Mapped[list[MetricDefinition]] = relationship(
        "MetricDefinition", back_populates="platform", lazy="raise"
    )
    capabilities: Mapped[list[SocialPlatformCapability]] = relationship(
        "SocialPlatformCapability", back_populates="platform", lazy="raise"
    )
    content_templates: Mapped[list[SocialContentTemplate]] = relationship(
        "SocialContentTemplate", back_populates="platform", lazy="raise"
    )
    accounts: Mapped[list[SocialAccount]] = relationship(
        "SocialAccount", back_populates="platform", lazy="raise"
    )
    publication_targets: Mapped[list[PublicationTarget]] = relationship(
        "PublicationTarget", back_populates="platform", lazy="raise"
    )
    generation_outputs: Mapped[list[AIGenerationOutput]] = relationship(
        "AIGenerationOutput", back_populates="platform", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"SocialPlatform(id={self.id!r}, code={self.code!r}, status={self.status!r})"

"""Typed setting registry and default model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, CheckConstraint, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import ARRAY, CITEXT, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.enums import SettingValueType
from cloud_content_hub.infrastructure.database.mixins import UACMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.setting import Setting


class SettingDefinition(UUIDPrimaryKeyMixin, UACMixin, Base):
    """Global catalog entry describing a typed, inheritable setting."""

    __tablename__ = "setting_definitions"
    __table_args__ = (
        CheckConstraint(
            "value_type IN ('boolean','integer','decimal','string','string_list','object')",
            name="ck_setting_definitions__value_type",
        ),
        UniqueConstraint("key", name="uq_setting_definitions__key"),
        {"comment": "Typed setting registry with defaults and validation metadata."},
    )

    key: Mapped[str] = mapped_column(CITEXT, nullable=False)
    value_type: Mapped[SettingValueType] = mapped_column(Text, nullable=False)
    allowed_scopes: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    default_value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    validation_schema: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    is_secret: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    description: Mapped[str] = mapped_column(Text, nullable=False)

    settings: Mapped[list[Setting]] = relationship(
        "Setting", back_populates="definition", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"SettingDefinition(id={self.id!r}, key={self.key!r})"

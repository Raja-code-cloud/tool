"""Notification retention policy helpers."""

from __future__ import annotations

from datetime import datetime

from cloud_content_hub.application.notifications.interfaces.notification_repository import (
    RetentionPolicy,
)
from cloud_content_hub.application.notifications.validators.notification_validator import (
    resolve_retention_expiry,
)


class RetentionService:
    """Resolves notification expiry from retention policies."""

    @staticmethod
    def resolve_expires_at(
        *,
        retention_policy: RetentionPolicy,
        reference_time: datetime | None = None,
    ) -> datetime | None:
        """Return the expires_at timestamp for a retention policy."""

        return resolve_retention_expiry(
            retention_policy=retention_policy,
            reference_time=reference_time,
        )

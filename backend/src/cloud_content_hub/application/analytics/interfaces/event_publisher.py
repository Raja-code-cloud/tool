"""Transactional event publisher port for analytics domain events."""

from __future__ import annotations

from typing import Protocol

from cloud_content_hub.application.analytics.events import AnalyticsDomainEvent
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class IAnalyticsEventPublisher(Protocol):
    """Persists analytics domain events through the transactional outbox."""

    async def publish(self, event: AnalyticsDomainEvent, *, unit_of_work: IUnitOfWork) -> None:
        """Enqueue a domain event in the same transaction as the originating change."""

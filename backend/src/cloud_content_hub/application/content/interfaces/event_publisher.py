"""Transactional event publisher port for content domain events."""

from __future__ import annotations

from typing import Protocol

from cloud_content_hub.application.content.events import ContentDomainEvent
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class IContentEventPublisher(Protocol):
    """Persists content domain events through the transactional outbox."""

    async def publish(self, event: ContentDomainEvent, *, unit_of_work: IUnitOfWork) -> None:
        """Enqueue a domain event in the same transaction as the originating change."""

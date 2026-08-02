"""Transactional event publisher port for search domain events."""

from __future__ import annotations

from typing import Protocol

from cloud_content_hub.application.search.events import SearchDomainEvent
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class ISearchEventPublisher(Protocol):
    """Persists search domain events through the transactional outbox."""

    async def publish(self, event: SearchDomainEvent, *, unit_of_work: IUnitOfWork) -> None:
        """Enqueue a domain event in the same transaction as the originating change."""

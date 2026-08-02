"""Transactional event publisher port for administration domain events."""

from __future__ import annotations

from typing import Protocol

from cloud_content_hub.application.administration.events import AdministrationDomainEvent
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class IAdministrationEventPublisher(Protocol):
    """Persists administration domain events through the transactional outbox."""

    async def publish(self, event: AdministrationDomainEvent, *, unit_of_work: IUnitOfWork) -> None:
        """Enqueue a domain event in the same transaction as the originating change."""

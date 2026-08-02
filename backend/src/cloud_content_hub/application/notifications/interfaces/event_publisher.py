"""Transactional event publisher port for notification domain events."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork

if TYPE_CHECKING:
    from cloud_content_hub.application.notifications.events import NotificationDomainEvent


class INotificationEventPublisher(Protocol):
    """Persists notification domain events through the transactional outbox."""

    async def publish(
        self,
        event: NotificationDomainEvent,
        *,
        unit_of_work: IUnitOfWork,
    ) -> None:
        """Enqueue a domain event in the same transaction as the originating change."""

"""Transactional event publisher port for asset domain events."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork

if TYPE_CHECKING:
    from cloud_content_hub.application.assets.events import AssetDomainEvent


class IAssetEventPublisher(Protocol):
    """Persists asset domain events through the transactional outbox."""

    async def publish(self, event: AssetDomainEvent, *, unit_of_work: IUnitOfWork) -> None:
        """Enqueue a domain event in the same transaction as the originating change."""

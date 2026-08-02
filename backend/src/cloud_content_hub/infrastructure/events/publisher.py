"""Outbox-backed event publisher adapters."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Protocol
from uuid import UUID

from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.context import correlation_id_var, request_id_var
from cloud_content_hub.infrastructure.events.models import EventMetadata, OutboxAppendRequest
from cloud_content_hub.infrastructure.events.outbox import OutboxRepository
from cloud_content_hub.infrastructure.events.registry import EventRegistry
from cloud_content_hub.infrastructure.events.tracing import build_event_headers
from cloud_content_hub.infrastructure.repositories.sqlalchemy.adapter_session import resolve_session

if TYPE_CHECKING:
    from cloud_content_hub.application.administration.events import AdministrationDomainEvent
    from cloud_content_hub.application.analytics.events import AnalyticsDomainEvent
    from cloud_content_hub.application.assets.events import AssetDomainEvent
    from cloud_content_hub.application.content.events import ContentDomainEvent
    from cloud_content_hub.application.notifications.events import NotificationDomainEvent


class OutboxEventPublisher:
    """Shared outbox append logic for module-specific publisher adapters."""

    def __init__(
        self,
        *,
        registry: EventRegistry,
        outbox: OutboxRepository,
    ) -> None:
        self._registry = registry
        self._outbox = outbox

    async def publish_event(self, event: object, *, unit_of_work: IUnitOfWork) -> UUID:
        serialization = self._registry.serialize(event)
        occurred_at = getattr(event, "occurred_at", None)
        if not isinstance(occurred_at, datetime):
            occurred_at = datetime.now(tz=UTC)

        actor_id = getattr(event, "actor_id", None)
        created_by = actor_id if isinstance(actor_id, UUID) else None
        headers = build_event_headers(
            metadata=EventMetadata(
                correlation_id=correlation_id_var.get(),
                request_id=request_id_var.get(),
            )
        )

        request = OutboxAppendRequest(
            workspace_id=serialization.workspace_id,
            organization_id=serialization.organization_id,
            aggregate_type=serialization.aggregate_type,
            aggregate_id=serialization.aggregate_id,
            event_type=serialization.event_type,
            event_version=serialization.event_version,
            payload=serialization.payload,
            headers=headers,
            occurred_at=occurred_at,
            available_at=occurred_at,
            created_by=created_by,
        )
        session = resolve_session(unit_of_work)
        return await self._outbox.append(session, request)


class AssetEventPublisher(OutboxEventPublisher):
    async def publish(self, event: AssetDomainEvent, *, unit_of_work: IUnitOfWork) -> None:
        await self.publish_event(event, unit_of_work=unit_of_work)


class ContentEventPublisher(OutboxEventPublisher):
    async def publish(self, event: ContentDomainEvent, *, unit_of_work: IUnitOfWork) -> None:
        await self.publish_event(event, unit_of_work=unit_of_work)


class NotificationEventPublisher(OutboxEventPublisher):
    async def publish(self, event: NotificationDomainEvent, *, unit_of_work: IUnitOfWork) -> None:
        await self.publish_event(event, unit_of_work=unit_of_work)


class AnalyticsEventPublisher(OutboxEventPublisher):
    async def publish(self, event: AnalyticsDomainEvent, *, unit_of_work: IUnitOfWork) -> None:
        await self.publish_event(event, unit_of_work=unit_of_work)


class AdministrationEventPublisher(OutboxEventPublisher):
    async def publish(self, event: AdministrationDomainEvent, *, unit_of_work: IUnitOfWork) -> None:
        await self.publish_event(event, unit_of_work=unit_of_work)


class EventPublisherBundle(Protocol):
    """Composition-root view of all module publisher adapters."""

    @property
    def assets(self) -> AssetEventPublisher: ...

    @property
    def content(self) -> ContentEventPublisher: ...

    @property
    def notifications(self) -> NotificationEventPublisher: ...

    @property
    def analytics(self) -> AnalyticsEventPublisher: ...

    @property
    def administration(self) -> AdministrationEventPublisher: ...

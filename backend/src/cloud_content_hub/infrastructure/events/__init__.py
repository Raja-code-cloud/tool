"""Transactional outbox event publishing infrastructure."""

from __future__ import annotations

from typing import Any

__all__ = [
    "EVENT_SCHEMA_VERSION",
    "AdministrationEventPublisher",
    "AnalyticsEventPublisher",
    "AssetEventPublisher",
    "CeleryAppBroker",
    "CeleryTaskBroker",
    "ContentEventPublisher",
    "EventDescriptor",
    "EventEnvelope",
    "EventError",
    "EventInfrastructureBundle",
    "EventMetadata",
    "EventPublisherBundleImpl",
    "EventPublishingConfig",
    "EventRegistry",
    "EventSerializationError",
    "NotificationEventPublisher",
    "OutboxAppendRequest",
    "OutboxDeliveryService",
    "OutboxDispatchError",
    "OutboxDispatchRecord",
    "OutboxDispatcher",
    "OutboxEventPublisher",
    "OutboxHealthCheck",
    "OutboxRepository",
    "OutboxRetryExhaustedError",
    "OutboxSerialization",
    "OutboxWriteError",
    "PlatformDeliverer",
    "PoisonMessageError",
    "RetryDecision",
    "RetryPolicy",
    "SqlAlchemyOutboxLagProbe",
    "UnknownEventTypeError",
    "create_default_registry",
    "create_event_infrastructure",
    "create_event_registry",
    "create_outbox_health_check",
    "envelope_from_record",
    "noop_platform_deliverer",
]


def __getattr__(name: str) -> Any:
    if name in {
        "EventPublishingConfig",
        "EventError",
        "EventSerializationError",
        "OutboxDispatchError",
        "OutboxRetryExhaustedError",
        "OutboxWriteError",
        "PoisonMessageError",
        "UnknownEventTypeError",
    }:
        from cloud_content_hub.infrastructure.events import config, exceptions

        return getattr(config if name == "EventPublishingConfig" else exceptions, name)

    if name in {
        "EVENT_SCHEMA_VERSION",
        "EventEnvelope",
        "EventMetadata",
        "OutboxAppendRequest",
        "OutboxDispatchRecord",
    }:
        from cloud_content_hub.infrastructure.events import models

        return getattr(models, name)

    if name in {
        "EventDescriptor",
        "EventRegistry",
        "OutboxSerialization",
        "create_default_registry",
    }:
        from cloud_content_hub.infrastructure.events import registry

        return getattr(registry, name)

    if name in {"OutboxRepository", "SqlAlchemyOutboxLagProbe"}:
        from cloud_content_hub.infrastructure.events import outbox

        return getattr(outbox, name)

    if name in {
        "AdministrationEventPublisher",
        "AnalyticsEventPublisher",
        "AssetEventPublisher",
        "ContentEventPublisher",
        "NotificationEventPublisher",
        "OutboxEventPublisher",
    }:
        from cloud_content_hub.infrastructure.events import publisher

        return getattr(publisher, name)

    if name in {
        "CeleryAppBroker",
        "CeleryTaskBroker",
        "OutboxDeliveryService",
        "OutboxDispatcher",
        "OutboxHealthCheck",
        "PlatformDeliverer",
        "RetryDecision",
        "RetryPolicy",
        "envelope_from_record",
        "noop_platform_deliverer",
    }:
        from cloud_content_hub.infrastructure.events import dispatcher

        return getattr(dispatcher, name)

    if name in {
        "EventInfrastructureBundle",
        "EventPublisherBundleImpl",
        "create_event_infrastructure",
        "create_event_registry",
        "create_outbox_health_check",
    }:
        from cloud_content_hub.infrastructure.events import factory

        return getattr(factory, name)

    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)

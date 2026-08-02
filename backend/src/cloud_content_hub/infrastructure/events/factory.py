"""Composition helpers for event publishing infrastructure."""

from __future__ import annotations

from dataclasses import dataclass

from opentelemetry.trace import Tracer

from cloud_content_hub.infrastructure.events.config import EventPublishingConfig
from cloud_content_hub.infrastructure.events.dispatcher import (
    CeleryAppBroker,
    CeleryTaskBroker,
    OutboxDeliveryService,
    OutboxDispatcher,
    OutboxHealthCheck,
    PlatformDeliverer,
    RetryPolicy,
    noop_platform_deliverer,
)
from cloud_content_hub.infrastructure.events.outbox import (
    OutboxRepository,
    SqlAlchemyOutboxLagProbe,
)
from cloud_content_hub.infrastructure.events.publisher import (
    AdministrationEventPublisher,
    AnalyticsEventPublisher,
    AssetEventPublisher,
    ContentEventPublisher,
    NotificationEventPublisher,
)
from cloud_content_hub.infrastructure.events.registry import EventRegistry, create_default_registry
from cloud_content_hub.infrastructure.observability.metrics import ObservabilityMetrics


@dataclass(frozen=True, slots=True)
class EventInfrastructureBundle:
    """Caller-owned event publishing components suitable for bootstrap wiring."""

    config: EventPublishingConfig
    registry: EventRegistry
    outbox: OutboxRepository
    lag_probe: SqlAlchemyOutboxLagProbe
    publishers: EventPublisherBundleImpl
    dispatcher: OutboxDispatcher
    delivery_service: OutboxDeliveryService
    retry_policy: RetryPolicy


@dataclass(frozen=True, slots=True)
class EventPublisherBundleImpl:
    assets: AssetEventPublisher
    content: ContentEventPublisher
    notifications: NotificationEventPublisher
    analytics: AnalyticsEventPublisher
    administration: AdministrationEventPublisher


def create_event_registry() -> EventRegistry:
    """Return the default domain event registry."""

    return create_default_registry()


def create_event_infrastructure(
    *,
    config: EventPublishingConfig | None = None,
    registry: EventRegistry | None = None,
    broker: CeleryTaskBroker | None = None,
    celery_app: object | None = None,
    deliverer: PlatformDeliverer | None = None,
    metrics: ObservabilityMetrics | None = None,
    tracer: Tracer | None = None,
) -> EventInfrastructureBundle:
    """Construct the standard outbox publishing stack without global side effects."""

    resolved_config = config or EventPublishingConfig()
    resolved_registry = registry or create_event_registry()
    resolved_broker = broker or CeleryAppBroker(_require_celery_app(celery_app))
    outbox = OutboxRepository()
    lag_probe = SqlAlchemyOutboxLagProbe()
    publishers = EventPublisherBundleImpl(
        assets=AssetEventPublisher(registry=resolved_registry, outbox=outbox),
        content=ContentEventPublisher(registry=resolved_registry, outbox=outbox),
        notifications=NotificationEventPublisher(registry=resolved_registry, outbox=outbox),
        analytics=AnalyticsEventPublisher(registry=resolved_registry, outbox=outbox),
        administration=AdministrationEventPublisher(registry=resolved_registry, outbox=outbox),
    )
    retry_policy = RetryPolicy(resolved_config)
    return EventInfrastructureBundle(
        config=resolved_config,
        registry=resolved_registry,
        outbox=outbox,
        lag_probe=lag_probe,
        publishers=publishers,
        dispatcher=OutboxDispatcher(
            outbox=outbox,
            registry=resolved_registry,
            broker=resolved_broker,
            config=resolved_config,
            metrics=metrics,
            tracer=tracer,
        ),
        delivery_service=OutboxDeliveryService(
            outbox=outbox,
            registry=resolved_registry,
            deliverer=deliverer or noop_platform_deliverer,
            config=resolved_config,
            retry_policy=retry_policy,
            metrics=metrics,
            tracer=tracer,
        ),
        retry_policy=retry_policy,
    )


def create_outbox_health_check(
    bundle: EventInfrastructureBundle,
    *,
    session_factory: object,
    name: str = "outbox_dispatch",
) -> OutboxHealthCheck:
    """Build an outbox lag readiness probe from an existing bundle."""

    return OutboxHealthCheck(
        session_factory=session_factory,  # type: ignore[arg-type]
        lag_probe=bundle.lag_probe,
        config=bundle.config,
        name=name,
    )


def _require_celery_app(celery_app: object | None) -> object:
    if celery_app is None:
        from cloud_content_hub.workers.celery_app import celery_app as default_app

        return default_app
    return celery_app

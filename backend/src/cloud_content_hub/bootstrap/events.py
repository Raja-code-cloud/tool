"""Event infrastructure wiring for the composition root."""

from __future__ import annotations

from celery import Celery

from cloud_content_hub.infrastructure.events.config import EventPublishingConfig
from cloud_content_hub.infrastructure.events.factory import (
    EventInfrastructureBundle,
    create_event_infrastructure,
    create_outbox_health_check,
)
from cloud_content_hub.infrastructure.observability.factory import ObservabilityBundle


def create_event_bundle(
    *,
    celery_app: Celery,
    observability: ObservabilityBundle,
    config: EventPublishingConfig | None = None,
) -> EventInfrastructureBundle:
    """Construct the transactional outbox and Celery producer stack."""

    return create_event_infrastructure(
        config=config or EventPublishingConfig(),
        celery_app=celery_app,
        metrics=observability.metrics,
        tracer=observability.tracer,
    )


def create_outbox_health_contributor(
    *,
    bundle: EventInfrastructureBundle,
    session_factory: object,
) -> object:
    """Build the outbox lag health contributor."""

    return create_outbox_health_check(bundle, session_factory=session_factory)

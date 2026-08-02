"""Outbox polling, Celery handoff, retry, and delivery orchestration."""

from __future__ import annotations

import math
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

import structlog
from opentelemetry.trace import Tracer
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_content_hub.infrastructure.events.config import EventPublishingConfig
from cloud_content_hub.infrastructure.events.exceptions import (
    OutboxRetryExhaustedError,
    PoisonMessageError,
    UnknownEventTypeError,
)
from cloud_content_hub.infrastructure.events.models import (
    EVENT_SCHEMA_VERSION,
    EventEnvelope,
    EventMetadata,
    OutboxDispatchRecord,
)
from cloud_content_hub.infrastructure.events.outbox import OutboxRepository
from cloud_content_hub.infrastructure.events.registry import EventRegistry
from cloud_content_hub.infrastructure.observability.health import HealthResult, HealthStatus
from cloud_content_hub.infrastructure.observability.metrics import ObservabilityMetrics
from cloud_content_hub.infrastructure.observability.tracing import background_span, client_span

logger = structlog.get_logger(__name__)

PlatformDeliverer = Callable[[EventEnvelope], Awaitable[None]]


class CeleryTaskBroker(Protocol):
    """Abstraction over Celery ``send_task`` for testability."""

    def enqueue(
        self,
        *,
        task_name: str,
        queue: str,
        kwargs: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> str:
        """Enqueue one delivery task and return the broker task id."""


class CeleryAppBroker:
    """Production Celery broker adapter."""

    def __init__(self, celery_app: Any) -> None:
        self._celery_app = celery_app

    def enqueue(
        self,
        *,
        task_name: str,
        queue: str,
        kwargs: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> str:
        send_task = self._celery_app.send_task
        async_result = send_task(
            task_name,
            kwargs=dict(kwargs),
            queue=queue,
            headers=dict(headers or {}),
        )
        return str(async_result.id)


def envelope_from_record(record: OutboxDispatchRecord) -> EventEnvelope:
    """Build a versioned wire envelope from a claimed outbox row."""

    metadata = EventMetadata(
        correlation_id=_header_str(record.headers, "correlation_id"),
        trace_id=_header_str(record.headers, "trace_id"),
        span_id=_header_str(record.headers, "span_id"),
        request_id=_header_str(record.headers, "request_id"),
    )
    return EventEnvelope(
        schema_version=EVENT_SCHEMA_VERSION,
        event_id=record.id,
        event_type=record.event_type,
        event_version=record.event_version,
        aggregate_type=record.aggregate_type,
        aggregate_id=record.aggregate_id,
        workspace_id=record.workspace_id,
        organization_id=record.organization_id,
        occurred_at=record.occurred_at,
        payload=record.payload,
        metadata=metadata,
        headers=dict(record.headers),
    )


@dataclass(frozen=True, slots=True)
class RetryDecision:
    """Outcome of classifying a failed dispatch attempt."""

    retry: bool
    reason_code: str
    reason_message: str
    available_at: datetime | None = None


class RetryPolicy:
    """Bounded exponential backoff with poison-message detection."""

    def __init__(self, config: EventPublishingConfig) -> None:
        self._config = config

    def classify_failure(
        self,
        record: OutboxDispatchRecord,
        error: Exception,
        *,
        now: datetime,
    ) -> RetryDecision:
        message = str(error)[:2048]
        next_attempt = record.attempt_count + 1

        if isinstance(error, PoisonMessageError | UnknownEventTypeError):
            return RetryDecision(
                retry=False,
                reason_code="poison_message",
                reason_message=message,
            )

        if (
            record.last_error == message
            and record.attempt_count + 1 >= self._config.poison_message_threshold
        ):
            return RetryDecision(
                retry=False,
                reason_code="poison_message",
                reason_message=f"Repeated failure: {message}",
            )

        if next_attempt >= self._config.max_attempts:
            return RetryDecision(
                retry=False,
                reason_code="retry_exhausted",
                reason_message=message,
            )

        delay = min(
            self._config.max_backoff_seconds,
            self._config.base_backoff_seconds
            * math.pow(self._config.backoff_multiplier, next_attempt - 1),
        )
        return RetryDecision(
            retry=True,
            reason_code="transient_failure",
            reason_message=message,
            available_at=now.replace() + _seconds_to_timedelta(delay),
        )


class OutboxDispatcher:
    """Polls due outbox rows and enqueues Celery delivery tasks."""

    def __init__(
        self,
        *,
        outbox: OutboxRepository,
        registry: EventRegistry,
        broker: CeleryTaskBroker,
        config: EventPublishingConfig,
        metrics: ObservabilityMetrics | None = None,
        tracer: Tracer | None = None,
    ) -> None:
        self._outbox = outbox
        self._registry = registry
        self._broker = broker
        self._config = config
        self._metrics = metrics
        self._tracer = tracer

    async def dispatch_batch(self, session: AsyncSession, *, now: datetime | None = None) -> int:
        """Claim and enqueue one batch of due outbox events."""

        effective_now = now or datetime.now(tz=UTC)
        records = await self._outbox.fetch_due(
            session,
            limit=self._config.batch_size,
            now=effective_now,
        )
        dispatched = 0
        for record in records:
            await self._enqueue_record(record)
            dispatched += 1
        if dispatched and self._metrics is not None:
            self._metrics.queue_depth.labels(queue=self._config.celery_queue).set(dispatched)
        return dispatched

    async def _enqueue_record(self, record: OutboxDispatchRecord) -> None:
        envelope = envelope_from_record(record)
        descriptor = self._registry.describe_by_name(record.event_type)
        queue = descriptor.celery_queue
        span_name = "outbox.dispatch"
        if self._tracer is None:
            self._broker.enqueue(
                task_name=self._config.celery_task_name,
                queue=queue,
                kwargs={"envelope": envelope.model_dump(mode="json")},
                headers=_trace_headers(envelope),
            )
            logger.info(
                "outbox_event_enqueued",
                event_id=str(record.id),
                event_type=record.event_type,
                queue=queue,
            )
            return

        with client_span(
            self._tracer,
            span_name,
            attributes={
                "event.id": str(record.id),
                "event.type": record.event_type,
                "messaging.destination": queue,
            },
        ):
            self._broker.enqueue(
                task_name=self._config.celery_task_name,
                queue=queue,
                kwargs={"envelope": envelope.model_dump(mode="json")},
                headers=_trace_headers(envelope),
            )
            logger.info(
                "outbox_event_enqueued",
                event_id=str(record.id),
                event_type=record.event_type,
                queue=queue,
            )


class OutboxDeliveryService:
    """Worker-side delivery, retry scheduling, and dead-letter handling."""

    def __init__(
        self,
        *,
        outbox: OutboxRepository,
        registry: EventRegistry,
        deliverer: PlatformDeliverer,
        config: EventPublishingConfig,
        retry_policy: RetryPolicy | None = None,
        metrics: ObservabilityMetrics | None = None,
        tracer: Tracer | None = None,
    ) -> None:
        self._outbox = outbox
        self._registry = registry
        self._deliverer = deliverer
        self._config = config
        self._retry_policy = retry_policy or RetryPolicy(config)
        self._metrics = metrics
        self._tracer = tracer

    async def deliver(
        self,
        session: AsyncSession,
        envelope: EventEnvelope,
        *,
        record: OutboxDispatchRecord | None = None,
    ) -> None:
        """Deliver one event to the platform adapter and finalize outbox state."""

        started = datetime.now(tz=UTC)
        dispatch_record = record or OutboxDispatchRecord(
            id=envelope.event_id,
            workspace_id=envelope.workspace_id,
            organization_id=envelope.organization_id,
            aggregate_type=envelope.aggregate_type,
            aggregate_id=envelope.aggregate_id,
            event_type=envelope.event_type,
            event_version=envelope.event_version,
            payload=envelope.payload,
            headers=envelope.headers,
            occurred_at=envelope.occurred_at,
            available_at=envelope.occurred_at,
            attempt_count=0,
            last_error=None,
        )

        try:
            self._registry.describe_by_name(envelope.event_type)
            await self._invoke_deliverer(envelope)
            await self._outbox.mark_published(session, envelope.event_id, published_at=started)
            self._record_outcome("success", envelope.event_type, started)
            logger.info(
                "outbox_event_delivered",
                event_id=str(envelope.event_id),
                event_type=envelope.event_type,
            )
        except Exception as error:
            await self._handle_failure(session, dispatch_record, error, now=started)
            raise

    async def _invoke_deliverer(self, envelope: EventEnvelope) -> None:
        if self._tracer is None:
            await self._deliverer(envelope)
            return
        with background_span(
            self._tracer,
            "outbox.deliver",
            attributes={
                "event.id": str(envelope.event_id),
                "event.type": envelope.event_type,
            },
        ):
            await self._deliverer(envelope)

    async def _handle_failure(
        self,
        session: AsyncSession,
        record: OutboxDispatchRecord,
        error: Exception,
        *,
        now: datetime,
    ) -> None:
        decision = self._retry_policy.classify_failure(record, error, now=now)
        self._record_outcome("failure", record.event_type, now)
        if self._metrics is not None:
            self._metrics.retries.labels(
                component="outbox",
                operation="deliver",
                reason=decision.reason_code,
            ).inc()

        if decision.retry and decision.available_at is not None:
            await self._outbox.schedule_retry(
                session,
                record.id,
                attempt_count=record.attempt_count + 1,
                available_at=decision.available_at,
                last_error=decision.reason_message,
            )
            logger.warning(
                "outbox_event_retry_scheduled",
                event_id=str(record.id),
                event_type=record.event_type,
                attempt_count=record.attempt_count + 1,
                reason=decision.reason_message,
            )
            return

        if record.workspace_id is not None:
            await self._outbox.move_to_dead_letter(
                session,
                record,
                reason_code=decision.reason_code,
                reason_message=decision.reason_message,
                failed_at=now,
            )
        else:
            await self._outbox.mark_terminal_failure(
                session,
                record.id,
                failed_at=now,
                last_error=decision.reason_message,
            )
            logger.error(
                "outbox_global_event_terminal_failure",
                event_id=str(record.id),
                event_type=record.event_type,
                reason=decision.reason_message,
            )

        msg = f"Outbox delivery failed terminally for {record.event_type}"
        raise OutboxRetryExhaustedError(msg) from error

    def _record_outcome(self, outcome: str, event_type: str, started: datetime) -> None:
        if self._metrics is None:
            return
        duration = max(0.0, (datetime.now(tz=UTC) - started).total_seconds())
        self._metrics.worker_jobs.labels(worker="outbox", job=event_type, outcome=outcome).inc()
        self._metrics.worker_duration.labels(worker="outbox", job=event_type).observe(duration)


class OutboxHealthCheck:
    """Readiness probe for outbox dispatch lag."""

    def __init__(
        self,
        *,
        session_factory: Callable[[], Awaitable[AsyncSession]],
        lag_probe: object,
        config: EventPublishingConfig,
        name: str = "outbox_dispatch",
    ) -> None:
        self._session_factory = session_factory
        self._lag_probe = lag_probe
        self._config = config
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def check(self) -> HealthResult:
        started = datetime.now(tz=UTC)
        session = await self._session_factory()
        try:
            oldest_age = await self._lag_probe.oldest_unpublished_age_seconds(session)  # type: ignore[attr-defined]
        finally:
            await session.close()

        if oldest_age is None:
            return HealthResult(
                name=self._name,
                status=HealthStatus.HEALTHY,
                duration_ms=_elapsed_ms(started),
                message="No unpublished outbox events",
            )

        status = (
            HealthStatus.HEALTHY
            if oldest_age <= self._config.dispatch_lag_warning_seconds
            else HealthStatus.DEGRADED
        )
        return HealthResult(
            name=self._name,
            status=status,
            duration_ms=_elapsed_ms(started),
            message="Outbox dispatch lag measured",
            details={"oldest_unpublished_age_seconds": round(oldest_age, 3)},
        )


def _header_str(headers: Mapping[str, Any], key: str) -> str | None:
    value = headers.get(key)
    return value if isinstance(value, str) else None


def _trace_headers(envelope: EventEnvelope) -> dict[str, str]:
    headers = dict(envelope.headers)
    if envelope.metadata.trace_id:
        headers.setdefault("trace_id", envelope.metadata.trace_id)
    if envelope.metadata.correlation_id:
        headers.setdefault("correlation_id", envelope.metadata.correlation_id)
    return {key: value for key, value in headers.items() if isinstance(value, str)}


def _seconds_to_timedelta(seconds: float) -> timedelta:
    return timedelta(seconds=seconds)


def _elapsed_ms(started: datetime) -> float:
    return max(0.0, (datetime.now(tz=UTC) - started).total_seconds() * 1000)


async def noop_platform_deliverer(_envelope: EventEnvelope) -> None:
    """Default platform adapter used until module-specific handlers are wired."""

    return None

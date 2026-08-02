"""Worker task execution primitives."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, TypeVar
from uuid import UUID

import structlog
from opentelemetry.trace import SpanKind, Tracer
from pydantic import BaseModel, ConfigDict, Field

from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.core.context import bind_request_context, clear_request_context
from cloud_content_hub.infrastructure.observability.metrics import ObservabilityMetrics
from cloud_content_hub.infrastructure.observability.tracing import (
    attach_context,
    background_span,
    current_trace_ids,
    detach_context,
)
from cloud_content_hub.workers.config import WorkerRuntimeConfig
from cloud_content_hub.workers.exceptions import (
    DeadLetterError,
    TransientWorkerError,
)
from cloud_content_hub.workers.retry import DeadLetterQueue, WorkerRetryPolicy
from cloud_content_hub.workers.routing import resolve_task_route

logger = structlog.get_logger(__name__)

ReturnT = TypeVar("ReturnT")


class WorkerTaskPayload(BaseModel):
    """Normalized Celery task payload consumed by worker handlers."""

    model_config = ConfigDict(frozen=True)

    workspace_id: UUID | None = None
    actor_id: UUID
    job_id: UUID | None = None
    resource_type: str | None = None
    resource_id: UUID | None = None
    idempotency_key: str | None = None
    attempt_count: int = 0
    last_error: str | None = None
    correlation_id: str | None = None
    request_id: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
    command: dict[str, Any] = Field(default_factory=dict)
    envelope: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class TaskExecutionContext:
    """Runtime metadata for one Celery task invocation."""

    task_name: str
    task_id: str
    queue: str
    retry_count: int
    headers: Mapping[str, str]
    payload: WorkerTaskPayload


class TransientWorkerRetrySignal(Exception):
    """Internal signal instructing Celery to retry a transient failure."""

    def __init__(
        self,
        *,
        countdown: float,
        reason_code: str,
        cause: BaseException,
    ) -> None:
        self.countdown = countdown
        self.reason_code = reason_code
        self.cause = cause
        super().__init__(str(cause))


WorkerHandler = Callable[[ActorContext, WorkerTaskPayload], Awaitable[object | None]]


def build_worker_actor(payload: WorkerTaskPayload) -> ActorContext:
    """Build a system actor context for background task execution."""

    from cloud_content_hub.infrastructure.events.registry import GLOBAL_AGGREGATE_ID

    return ActorContext(
        user_id=payload.actor_id,
        workspace_id=payload.workspace_id or GLOBAL_AGGREGATE_ID,
        permissions=frozenset({"*"}),
    )


def build_task_payload(raw_payload: Mapping[str, Any]) -> WorkerTaskPayload:
    """Parse a raw Celery kwargs mapping into a typed payload."""

    return WorkerTaskPayload.model_validate(dict(raw_payload))


def build_execution_context(
    *,
    task_name: str,
    task_id: str,
    retry_count: int,
    headers: Mapping[str, str] | None,
    raw_payload: Mapping[str, Any],
    default_queue: str,
) -> TaskExecutionContext:
    """Construct execution context from Celery request metadata."""

    payload = build_task_payload(raw_payload)
    route = resolve_task_route(task_name, default_queue=default_queue)
    merged_headers = dict(headers or {})
    correlation_id = payload.correlation_id or merged_headers.get("correlation_id")
    request_id = payload.request_id or merged_headers.get("request_id")
    trace_id = payload.trace_id or merged_headers.get("trace_id")
    span_id = payload.span_id or merged_headers.get("span_id")
    normalized_payload = payload.model_copy(
        update={
            "correlation_id": correlation_id,
            "request_id": request_id,
            "trace_id": trace_id,
            "span_id": span_id,
            "attempt_count": max(payload.attempt_count, retry_count),
        }
    )
    return TaskExecutionContext(
        task_name=task_name,
        task_id=task_id,
        queue=route.queue,
        retry_count=retry_count,
        headers=merged_headers,
        payload=normalized_payload,
    )


class WorkerTaskRunner:
    """Executes worker tasks with observability, retries, and dead-letter support."""

    def __init__(
        self,
        *,
        config: WorkerRuntimeConfig,
        retry_policy: WorkerRetryPolicy,
        dead_letter_queue: DeadLetterQueue,
        dispatch: Callable[[TaskExecutionContext], Awaitable[object | None]],
        metrics: ObservabilityMetrics | None = None,
        tracer: Tracer | None = None,
    ) -> None:
        self._config = config
        self._retry_policy = retry_policy
        self._dead_letter_queue = dead_letter_queue
        self._dispatch = dispatch
        self._metrics = metrics
        self._tracer = tracer

    def run_sync(self, context: TaskExecutionContext) -> object | None:
        """Execute one task from a synchronous Celery worker process."""

        return asyncio.run(self.run(context))

    async def run(self, context: TaskExecutionContext) -> object | None:
        """Execute one task with metrics, tracing, logging, and retry handling."""

        started = datetime.now(tz=UTC)
        correlation_id = context.payload.correlation_id or context.task_id
        request_id = context.payload.request_id or context.task_id
        context_tokens = bind_request_context(request_id, correlation_id)
        trace_token = None
        carrier = {
            key: value
            for key, value in {
                "traceparent": _build_traceparent(
                    context.payload.trace_id,
                    context.payload.span_id,
                ),
                "correlation_id": correlation_id,
                "request_id": request_id,
            }.items()
            if value is not None
        }
        if carrier:
            trace_token = attach_context(carrier)

        bound_logger = logger.bind(
            task_name=context.task_name,
            task_id=context.task_id,
            queue=context.queue,
            correlation_id=correlation_id,
            request_id=request_id,
            workspace_id=(
                str(context.payload.workspace_id) if context.payload.workspace_id else None
            ),
            job_id=str(context.payload.job_id) if context.payload.job_id else None,
        )
        bound_logger.info("worker_task_started", retry_count=context.retry_count)

        try:
            result = await self._execute(context)
        except TransientWorkerRetrySignal:
            raise
        except Exception as error:
            await self._handle_failure(context, error, started=started, bound_logger=bound_logger)
            raise
        else:
            self._record_outcome(context.task_name, "success", started)
            bound_logger.info("worker_task_succeeded")
            return result
        finally:
            if trace_token is not None:
                detach_context(trace_token)
            clear_request_context(context_tokens)

    async def _execute(self, context: TaskExecutionContext) -> object | None:
        if self._tracer is None:
            return await self._dispatch(context)

        with background_span(
            self._tracer,
            f"worker.{context.task_name}",
            attributes={
                "task.name": context.task_name,
                "task.id": context.task_id,
                "messaging.destination": context.queue,
                "workspace.id": str(context.payload.workspace_id),
            },
            kind=SpanKind.CONSUMER,
        ):
            return await self._dispatch(context)

    async def _handle_failure(
        self,
        context: TaskExecutionContext,
        error: Exception,
        *,
        started: datetime,
        bound_logger: structlog.stdlib.BoundLogger,
    ) -> None:
        self._record_outcome(context.task_name, "failure", started)
        if self._metrics is not None:
            self._metrics.retries.labels(
                component="worker",
                operation=context.task_name,
                reason=type(error).__name__,
            ).inc()

        decision = self._retry_policy.classify_failure(
            task_name=context.task_name,
            attempt_count=context.payload.attempt_count,
            last_error=context.payload.last_error,
            error=error,
        )
        bound_logger.warning(
            "worker_task_failed",
            reason_code=decision.reason_code,
            retry=decision.retry,
            error_type=type(error).__name__,
        )

        if decision.retry and decision.backoff_seconds is not None:
            retry_cause = (
                error
                if isinstance(error, TransientWorkerError)
                else TransientWorkerError(detail=decision.reason_message)
            )
            raise TransientWorkerRetrySignal(
                countdown=decision.backoff_seconds,
                reason_code=decision.reason_code,
                cause=retry_cause,
            ) from error

        await self._dead_letter_queue.enqueue(
            task_name=context.task_name,
            payload=context.payload.model_dump(mode="json"),
            reason_code=decision.reason_code,
            reason_message=decision.reason_message,
        )
        raise DeadLetterError(detail=decision.reason_message) from error

    def _record_outcome(self, task_name: str, outcome: str, started: datetime) -> None:
        if self._metrics is None:
            return
        duration = max(0.0, (datetime.now(tz=UTC) - started).total_seconds())
        self._metrics.worker_jobs.labels(worker="celery", job=task_name, outcome=outcome).inc()
        self._metrics.worker_duration.labels(worker="celery", job=task_name).observe(duration)


def _build_traceparent(trace_id: str | None, span_id: str | None) -> str | None:
    if trace_id is None or span_id is None:
        resolved_trace_id, resolved_span_id = current_trace_ids()
        trace_id = trace_id or resolved_trace_id
        span_id = span_id or resolved_span_id
    if trace_id is None or span_id is None:
        return None
    return f"00-{trace_id}-{span_id}-01"

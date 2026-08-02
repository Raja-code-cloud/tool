"""Shared Celery task registration helpers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from cloud_content_hub.infrastructure.events.models import EventEnvelope
from cloud_content_hub.infrastructure.events.registry import GLOBAL_AGGREGATE_ID
from cloud_content_hub.workers.base import (
    TaskExecutionContext,
    TransientWorkerRetrySignal,
    WorkerTaskPayload,
    build_execution_context,
)
from cloud_content_hub.workers.factory import WorkerBundle

_bundle: WorkerBundle | None = None


def get_worker_bundle() -> WorkerBundle:
    """Return the process-scoped worker bundle, creating it lazily."""

    global _bundle
    if _bundle is None:
        from cloud_content_hub.bootstrap.container import Container
        from cloud_content_hub.core.config import load_settings
        from cloud_content_hub.workers.factory import create_worker_bundle

        _bundle = create_worker_bundle(Container.create(load_settings()))
    return _bundle


def reset_worker_bundle(bundle: WorkerBundle | None = None) -> None:
    """Replace or clear the cached worker bundle (for tests)."""

    global _bundle
    _bundle = bundle


def execute_worker_task(task: Any, raw_payload: Mapping[str, Any]) -> object | None:
    """Execute one Celery task through the worker runner."""

    bundle = get_worker_bundle()
    context = _build_context(task, raw_payload, default_queue=bundle.config.default_queue)
    try:
        return bundle.runner.run_sync(context)
    except TransientWorkerRetrySignal as exc:
        raise task.retry(countdown=max(1, int(exc.countdown)), exc=exc.cause) from exc.cause


def register_worker_task(name: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    """Decorator registering a Celery task with shared worker execution."""

    def decorator(func: Callable[..., object]) -> Callable[..., object]:
        from cloud_content_hub.workers.celery_app import celery_app

        @celery_app.task(bind=True, name=name)
        def wrapper(task: Any, *args: object, **kwargs: object) -> object | None:
            _ = args
            payload = _normalize_payload(name, kwargs)
            return execute_worker_task(task, payload)

        return wrapper

    return decorator


def _build_context(
    task: Any,
    raw_payload: Mapping[str, Any],
    *,
    default_queue: str,
) -> TaskExecutionContext:
    return build_execution_context(
        task_name=task.name,
        task_id=str(task.request.id),
        retry_count=int(task.request.retries),
        headers=_string_headers(task.request.headers),
        raw_payload=raw_payload,
        default_queue=default_queue,
    )


def _string_headers(headers: Mapping[str, Any] | None) -> dict[str, str]:
    if headers is None:
        return {}
    return {str(key): str(value) for key, value in headers.items() if value is not None}


def _normalize_payload(task_name: str, kwargs: Mapping[str, Any]) -> dict[str, Any]:
    if task_name.endswith("deliver_outbox_event"):
        return _envelope_payload(kwargs)
    return dict(kwargs)


def _envelope_payload(kwargs: Mapping[str, Any]) -> dict[str, Any]:
    envelope_raw = kwargs.get("envelope")
    if envelope_raw is None:
        msg = "deliver_outbox_event requires an envelope keyword argument."
        raise ValueError(msg)
    envelope = EventEnvelope.model_validate(envelope_raw)
    return WorkerTaskPayload(
        workspace_id=envelope.workspace_id,
        actor_id=GLOBAL_AGGREGATE_ID,
        correlation_id=envelope.metadata.correlation_id,
        request_id=envelope.metadata.request_id,
        trace_id=envelope.metadata.trace_id,
        span_id=envelope.metadata.span_id,
        envelope=envelope.model_dump(mode="json"),
    ).model_dump(mode="json")

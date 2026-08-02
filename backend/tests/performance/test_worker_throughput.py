"""Worker throughput and dispatch latency validation."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.workers.base import (
    TaskExecutionContext,
    WorkerTaskPayload,
    build_worker_actor,
)
from cloud_content_hub.workers.dispatcher import TaskDispatcher, WorkerHandlerRegistry
from cloud_content_hub.workers.routing import resolve_task_route
from tests.performance.helpers.metrics import collect_latencies, collect_latencies_sync
from tests.performance.helpers.targets import PERFORMANCE_TARGETS, assert_within_target

pytestmark = pytest.mark.performance


@pytest.fixture
def worker_payload() -> WorkerTaskPayload:
    return WorkerTaskPayload(
        workspace_id=uuid4(),
        actor_id=uuid4(),
        job_id=uuid4(),
        resource_type="asset",
        resource_id=uuid4(),
        command={"action": "noop"},
    )


@pytest.fixture
def worker_context(worker_payload: WorkerTaskPayload) -> TaskExecutionContext:
    route = resolve_task_route("cloud_content_hub.tasks.cleanup_temp_files")
    return TaskExecutionContext(
        task_name="cloud_content_hub.tasks.cleanup_temp_files",
        task_id="perf-task-1",
        queue=route.queue,
        retry_count=0,
        headers={"correlation_id": "perf-corr"},
        payload=worker_payload,
    )


@pytest.mark.asyncio
async def test_task_dispatcher_throughput(worker_context: TaskExecutionContext) -> None:
    handler = AsyncMock(return_value=None)
    registry = WorkerHandlerRegistry(
        {"cloud_content_hub.tasks.cleanup_temp_files": handler},
    )
    dispatcher = TaskDispatcher(registry)

    async def dispatch_once() -> None:
        await dispatcher.dispatch(worker_context)

    stats = await collect_latencies(
        label="TaskDispatcher.dispatch",
        iterations=200,
        operation=dispatch_once,
    )
    assert handler.await_count == 200
    assert_within_target(stats, p95_seconds=0.010, label="worker dispatch")


@pytest.mark.asyncio
async def test_worker_actor_construction_latency(worker_payload: WorkerTaskPayload) -> None:
    def build_once() -> None:
        _build_actor(worker_payload)

    stats = collect_latencies_sync(
        label="build_worker_actor",
        iterations=500,
        operation=build_once,
    )
    assert_within_target(stats, p95_seconds=0.001, label="worker actor build")


def test_retry_policy_classification_throughput() -> None:
    from cloud_content_hub.core.errors import DependencyUnavailableError
    from cloud_content_hub.workers.config import WorkerRetryConfig
    from cloud_content_hub.workers.retry import WorkerRetryPolicy

    policy = WorkerRetryPolicy(WorkerRetryConfig())

    def classify_once() -> None:
        policy.classify_failure(
            task_name="cloud_content_hub.tasks.upload_asset",
            attempt_count=1,
            last_error="timeout",
            error=DependencyUnavailableError(detail="redis unavailable"),
        )

    stats = collect_latencies_sync(
        label="WorkerRetryPolicy.classify_failure",
        iterations=1000,
        operation=classify_once,
    )
    assert_within_target(stats, p95_seconds=0.001, label="retry classification")


@pytest.mark.asyncio
async def test_notification_delivery_handler_dispatch(
    worker_payload: WorkerTaskPayload,
) -> None:
    route = resolve_task_route("cloud_content_hub.tasks.deliver_notification")
    context = TaskExecutionContext(
        task_name="cloud_content_hub.tasks.deliver_notification",
        task_id="perf-notify-1",
        queue=route.queue,
        retry_count=0,
        headers={"correlation_id": "perf-corr"},
        payload=worker_payload,
    )
    handler = AsyncMock(return_value=None)
    registry = WorkerHandlerRegistry(
        {"cloud_content_hub.tasks.deliver_notification": handler},
    )
    dispatcher = TaskDispatcher(registry)

    stats = await collect_latencies(
        label="deliver_notification dispatch",
        iterations=100,
        operation=lambda: dispatcher.dispatch(context),
    )
    assert_within_target(stats, p95_seconds=PERFORMANCE_TARGETS.api_crud_p95_seconds)


def _build_actor(payload: WorkerTaskPayload) -> ActorContext:
    actor = build_worker_actor(payload)
    assert actor.has_permission("assets:write") is True
    return actor

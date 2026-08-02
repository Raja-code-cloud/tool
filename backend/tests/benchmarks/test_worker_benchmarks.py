"""Worker runtime micro-benchmarks."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from cloud_content_hub.workers.base import TaskExecutionContext, WorkerTaskPayload
from cloud_content_hub.workers.dispatcher import TaskDispatcher, WorkerHandlerRegistry
from cloud_content_hub.workers.routing import resolve_task_route

pytestmark = pytest.mark.benchmark


@pytest.fixture
def dispatch_context() -> TaskExecutionContext:
    payload = WorkerTaskPayload(
        workspace_id=uuid4(),
        actor_id=uuid4(),
        job_id=uuid4(),
        command={"action": "noop"},
    )
    route = resolve_task_route("cloud_content_hub.tasks.import_analytics")
    return TaskExecutionContext(
        task_name="cloud_content_hub.tasks.import_analytics",
        task_id="bench-analytics",
        queue=route.queue,
        retry_count=0,
        headers={"correlation_id": "bench"},
        payload=payload,
    )


@pytest.mark.asyncio
async def test_benchmark_analytics_import_dispatch(
    benchmark: Any,
    dispatch_context: TaskExecutionContext,
) -> None:
    handler = AsyncMock(return_value=None)
    registry = WorkerHandlerRegistry(
        {"cloud_content_hub.tasks.import_analytics": handler},
    )
    dispatcher = TaskDispatcher(registry)

    async def run() -> None:
        await dispatcher.dispatch(dispatch_context)

    await benchmark.pedantic(run, rounds=20, iterations=1)


def test_benchmark_task_route_resolution(benchmark: Any) -> None:
    task_names = (
        "cloud_content_hub.tasks.upload_asset",
        "cloud_content_hub.tasks.generate_content",
        "cloud_content_hub.tasks.publish_content",
        "cloud_content_hub.tasks.deliver_notification",
        "cloud_content_hub.tasks.execute_scheduled_publish",
        "cloud_content_hub.deliver_outbox_event",
    )

    def run() -> None:
        for task_name in task_names:
            route = resolve_task_route(task_name)
            assert route.queue

    benchmark(run)

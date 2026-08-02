"""Unit tests for worker task registration and dispatch."""

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
from cloud_content_hub.workers.exceptions import WorkerTaskNotFoundError
from cloud_content_hub.workers.routing import resolve_task_route


@pytest.fixture
def actor_id():
    return uuid4()


@pytest.fixture
def workspace_id():
    return uuid4()


@pytest.fixture
def payload(workspace_id, actor_id) -> WorkerTaskPayload:
    return WorkerTaskPayload(
        workspace_id=workspace_id,
        actor_id=actor_id,
        job_id=uuid4(),
        command={"action": "noop"},
    )


@pytest.fixture
def context(payload: WorkerTaskPayload) -> TaskExecutionContext:
    route = resolve_task_route("cloud_content_hub.tasks.cleanup_temp_files")
    return TaskExecutionContext(
        task_name="cloud_content_hub.tasks.cleanup_temp_files",
        task_id="task-123",
        queue=route.queue,
        retry_count=0,
        headers={"correlation_id": "corr-1"},
        payload=payload,
    )


def test_build_worker_actor_grants_wildcard_permissions(payload: WorkerTaskPayload) -> None:
    actor = build_worker_actor(payload)

    assert actor.permissions == frozenset({"*"})
    assert actor.has_permission("assets:write") is True
    assert actor.has_permission("publishing:delete") is True


@pytest.mark.asyncio
async def test_task_dispatcher_invokes_registered_handler(
    context: TaskExecutionContext,
    actor_id,
    workspace_id,
) -> None:
    handler = AsyncMock(return_value=None)
    registry = WorkerHandlerRegistry(
        {"cloud_content_hub.tasks.cleanup_temp_files": handler},
    )
    dispatcher = TaskDispatcher(registry)

    await dispatcher.dispatch(context)

    handler.assert_awaited_once()
    actor_arg: ActorContext = handler.await_args.args[0]
    assert actor_arg.user_id == actor_id
    assert actor_arg.workspace_id == workspace_id


def test_task_dispatcher_raises_for_unknown_task(context: TaskExecutionContext) -> None:
    dispatcher = TaskDispatcher(WorkerHandlerRegistry())

    with pytest.raises(WorkerTaskNotFoundError):
        import asyncio

        asyncio.run(dispatcher.dispatch(context))


@pytest.mark.asyncio
async def test_celery_task_catalog_is_registered() -> None:
    from cloud_content_hub.workers.celery_app import celery_app

    registered = set(celery_app.tasks.keys())

    assert "cloud_content_hub.tasks.upload_asset" in registered
    assert "cloud_content_hub.deliver_outbox_event" in registered
    assert "cloud_content_hub.tasks.cleanup_outbox" in registered


def test_worker_handler_registry_lists_task_names() -> None:
    registry = WorkerHandlerRegistry(
        {
            "cloud_content_hub.tasks.upload_asset": AsyncMock(),
            "cloud_content_hub.tasks.generate_content": AsyncMock(),
        }
    )

    assert registry.contains("cloud_content_hub.tasks.upload_asset") is True
    assert registry.task_names() == (
        "cloud_content_hub.tasks.generate_content",
        "cloud_content_hub.tasks.upload_asset",
    )
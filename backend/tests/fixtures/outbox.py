"""Outbox inspection and synchronous drain helpers for workflow tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cloud_content_hub.bootstrap.container import Container
from cloud_content_hub.infrastructure.database.models.outbox_event import OutboxEvent
from cloud_content_hub.infrastructure.events.testing.fakes import FakeCeleryBroker
from cloud_content_hub.workers.base import TaskExecutionContext, WorkerTaskPayload
from cloud_content_hub.workers.factory import create_worker_bundle
from cloud_content_hub.workers.routing import resolve_task_route


async def query_outbox_events(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    workspace_id: UUID,
    event_type: str | None = None,
) -> list[OutboxEvent]:
    """Return persisted outbox rows for assertions."""

    async with session_factory() as session:
        statement = select(OutboxEvent).where(OutboxEvent.workspace_id == workspace_id)
        if event_type is not None:
            statement = statement.where(OutboxEvent.event_type == event_type)
        statement = statement.order_by(OutboxEvent.created_at.asc())
        return list((await session.scalars(statement)).all())


async def drain_outbox(
    container: Container,
    *,
    broker: FakeCeleryBroker,
    now: datetime | None = None,
) -> int:
    """Dispatch due outbox rows and execute recorded Celery tasks synchronously."""

    resolved_now = now or datetime.now(tz=UTC)
    worker_bundle = create_worker_bundle(container)
    dispatched = 0

    async with container.session_factory() as session:
        dispatched = await container.events.dispatcher.dispatch_batch(session, now=resolved_now)
        await session.commit()

    for task in broker.tasks:
        route = resolve_task_route(task["task_name"])
        payload = WorkerTaskPayload.model_validate(task["kwargs"]["payload"])
        context = TaskExecutionContext(
            task_name=task["task_name"],
            task_id=task["task_id"],
            queue=route.queue,
            retry_count=0,
            headers=dict(task["headers"]),
            payload=payload,
        )
        await worker_bundle.dispatcher.dispatch(context)

    return dispatched

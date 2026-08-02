"""Dispatch worker tasks to registered application handlers."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import Any

import structlog

from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.workers.base import (
    TaskExecutionContext,
    WorkerHandler,
    WorkerTaskPayload,
    build_worker_actor,
)
from cloud_content_hub.workers.exceptions import WorkerTaskNotFoundError

logger = structlog.get_logger(__name__)


class WorkerHandlerRegistry:
    """Registry mapping Celery task names to async worker handlers."""

    def __init__(self, handlers: Mapping[str, WorkerHandler] | None = None) -> None:
        self._handlers: dict[str, WorkerHandler] = dict(handlers or {})

    def register(self, task_name: str, handler: WorkerHandler) -> None:
        """Register one handler for a task name."""

        self._handlers[task_name] = handler

    def get(self, task_name: str) -> WorkerHandler:
        """Return the handler registered for a task name."""

        handler = self._handlers.get(task_name)
        if handler is None:
            raise WorkerTaskNotFoundError(
                detail=f"No worker handler registered for task '{task_name}'.",
                parameters={"task_name": task_name},
            )
        return handler

    def contains(self, task_name: str) -> bool:
        """Return whether a handler is registered."""

        return task_name in self._handlers

    def task_names(self) -> tuple[str, ...]:
        """Return registered task names."""

        return tuple(sorted(self._handlers))


class TaskDispatcher:
    """Routes worker task execution to application handlers."""

    def __init__(self, registry: WorkerHandlerRegistry) -> None:
        self._registry = registry

    async def dispatch(self, context: TaskExecutionContext) -> object | None:
        """Execute the handler registered for the task."""

        handler = self._registry.get(context.task_name)
        actor = build_worker_actor(context.payload)
        logger.debug(
            "worker_dispatching_handler",
            task_name=context.task_name,
            handler=getattr(handler, "__qualname__", type(handler).__name__),
        )
        return await handler(actor, context.payload)

    def bind(self, task_name: str, handler: WorkerHandler) -> None:
        """Register a handler at runtime."""

        self._registry.register(task_name, handler)


def handler_adapter(
    handler: Callable[[ActorContext, Any], Awaitable[object | None]],
    *,
    command_builder: Callable[[WorkerTaskPayload], Any],
) -> WorkerHandler:
    """Adapt an application handler accepting (actor, command) to worker shape."""

    async def _invoke(actor: ActorContext, payload: WorkerTaskPayload) -> object | None:
        command = command_builder(payload)
        return await handler(actor, command)

    return _invoke

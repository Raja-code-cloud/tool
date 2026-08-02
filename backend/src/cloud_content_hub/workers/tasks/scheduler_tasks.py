"""Scheduler Celery tasks."""

from __future__ import annotations

from cloud_content_hub.workers.tasks._registry import register_worker_task


@register_worker_task("cloud_content_hub.tasks.execute_scheduled_publish")
def execute_scheduled_publish(**payload: object) -> None:
    """Execute a scheduled publication."""


@register_worker_task("cloud_content_hub.tasks.execute_scheduled_analytics")
def execute_scheduled_analytics(**payload: object) -> None:
    """Execute a scheduled analytics refresh."""


@register_worker_task("cloud_content_hub.tasks.execute_scheduled_cleanup")
def execute_scheduled_cleanup(**payload: object) -> None:
    """Execute a scheduled maintenance cleanup."""

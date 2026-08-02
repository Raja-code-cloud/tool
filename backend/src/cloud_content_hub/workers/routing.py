"""Celery queue routing for worker tasks."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from cloud_content_hub.application.shared.interfaces.job_queue import JobQueueName


@dataclass(frozen=True, slots=True)
class TaskRoute:
    """Resolved routing metadata for one worker task."""

    task_name: str
    queue: str
    category: str


_TASK_ROUTES: dict[str, TaskRoute] = {
    "cloud_content_hub.tasks.upload_asset": TaskRoute(
        "cloud_content_hub.tasks.upload_asset", JobQueueName.MEDIA, "asset"
    ),
    "cloud_content_hub.tasks.replace_asset": TaskRoute(
        "cloud_content_hub.tasks.replace_asset", JobQueueName.MEDIA, "asset"
    ),
    "cloud_content_hub.tasks.delete_asset": TaskRoute(
        "cloud_content_hub.tasks.delete_asset", JobQueueName.MEDIA, "asset"
    ),
    "cloud_content_hub.tasks.restore_asset": TaskRoute(
        "cloud_content_hub.tasks.restore_asset", JobQueueName.MEDIA, "asset"
    ),
    "cloud_content_hub.tasks.virus_scan": TaskRoute(
        "cloud_content_hub.tasks.virus_scan", JobQueueName.MEDIA, "asset"
    ),
    "cloud_content_hub.tasks.metadata_extraction": TaskRoute(
        "cloud_content_hub.tasks.metadata_extraction", JobQueueName.MEDIA, "asset"
    ),
    "cloud_content_hub.tasks.generate_content": TaskRoute(
        "cloud_content_hub.tasks.generate_content", JobQueueName.AI, "content"
    ),
    "cloud_content_hub.tasks.regenerate_content": TaskRoute(
        "cloud_content_hub.tasks.regenerate_content", JobQueueName.AI, "content"
    ),
    "cloud_content_hub.tasks.duplicate_content": TaskRoute(
        "cloud_content_hub.tasks.duplicate_content", JobQueueName.MAINTENANCE, "content"
    ),
    "cloud_content_hub.tasks.archive_content": TaskRoute(
        "cloud_content_hub.tasks.archive_content", JobQueueName.MAINTENANCE, "content"
    ),
    "cloud_content_hub.tasks.publish_content": TaskRoute(
        "cloud_content_hub.tasks.publish_content", JobQueueName.MAINTENANCE, "publishing"
    ),
    "cloud_content_hub.tasks.retry_publish": TaskRoute(
        "cloud_content_hub.tasks.retry_publish", JobQueueName.MAINTENANCE, "publishing"
    ),
    "cloud_content_hub.tasks.cancel_publish": TaskRoute(
        "cloud_content_hub.tasks.cancel_publish", JobQueueName.MAINTENANCE, "publishing"
    ),
    "cloud_content_hub.tasks.verify_publish_status": TaskRoute(
        "cloud_content_hub.tasks.verify_publish_status", JobQueueName.MAINTENANCE, "publishing"
    ),
    "cloud_content_hub.tasks.import_analytics": TaskRoute(
        "cloud_content_hub.tasks.import_analytics", JobQueueName.MAINTENANCE, "analytics"
    ),
    "cloud_content_hub.tasks.refresh_dashboard": TaskRoute(
        "cloud_content_hub.tasks.refresh_dashboard", JobQueueName.MAINTENANCE, "analytics"
    ),
    "cloud_content_hub.tasks.archive_snapshot": TaskRoute(
        "cloud_content_hub.tasks.archive_snapshot", JobQueueName.MAINTENANCE, "analytics"
    ),
    "cloud_content_hub.tasks.deliver_notification": TaskRoute(
        "cloud_content_hub.tasks.deliver_notification", JobQueueName.NOTIFICATION, "notification"
    ),
    "cloud_content_hub.tasks.retry_notification": TaskRoute(
        "cloud_content_hub.tasks.retry_notification", JobQueueName.NOTIFICATION, "notification"
    ),
    "cloud_content_hub.tasks.cleanup_notifications": TaskRoute(
        "cloud_content_hub.tasks.cleanup_notifications", JobQueueName.NOTIFICATION, "notification"
    ),
    "cloud_content_hub.tasks.cleanup_temp_files": TaskRoute(
        "cloud_content_hub.tasks.cleanup_temp_files", JobQueueName.MAINTENANCE, "maintenance"
    ),
    "cloud_content_hub.tasks.cleanup_expired_tokens": TaskRoute(
        "cloud_content_hub.tasks.cleanup_expired_tokens", JobQueueName.MAINTENANCE, "maintenance"
    ),
    "cloud_content_hub.tasks.cleanup_soft_deletes": TaskRoute(
        "cloud_content_hub.tasks.cleanup_soft_deletes", JobQueueName.MAINTENANCE, "maintenance"
    ),
    "cloud_content_hub.tasks.cleanup_outbox": TaskRoute(
        "cloud_content_hub.tasks.cleanup_outbox", JobQueueName.MAINTENANCE, "maintenance"
    ),
    "cloud_content_hub.tasks.cleanup_failed_jobs": TaskRoute(
        "cloud_content_hub.tasks.cleanup_failed_jobs", JobQueueName.MAINTENANCE, "maintenance"
    ),
    "cloud_content_hub.tasks.execute_scheduled_publish": TaskRoute(
        "cloud_content_hub.tasks.execute_scheduled_publish", JobQueueName.MAINTENANCE, "scheduler"
    ),
    "cloud_content_hub.tasks.execute_scheduled_analytics": TaskRoute(
        "cloud_content_hub.tasks.execute_scheduled_analytics", JobQueueName.MAINTENANCE, "scheduler"
    ),
    "cloud_content_hub.tasks.execute_scheduled_cleanup": TaskRoute(
        "cloud_content_hub.tasks.execute_scheduled_cleanup", JobQueueName.MAINTENANCE, "scheduler"
    ),
    "cloud_content_hub.deliver_outbox_event": TaskRoute(
        "cloud_content_hub.deliver_outbox_event", JobQueueName.MAINTENANCE, "outbox"
    ),
}


def resolve_task_route(task_name: str, *, default_queue: str = "maintenance") -> TaskRoute:
    """Return routing metadata for a task, falling back to the default queue."""

    route = _TASK_ROUTES.get(task_name)
    if route is not None:
        return route
    return TaskRoute(task_name=task_name, queue=default_queue, category="unknown")


def build_celery_task_routes(default_queue: str = "maintenance") -> dict[str, Mapping[str, str]]:
    """Build Celery ``task_routes`` mapping from the task catalog."""

    return {task_name: {"queue": route.queue} for task_name, route in _TASK_ROUTES.items()}


def list_task_routes() -> tuple[TaskRoute, ...]:
    """Return all registered task routes."""

    return tuple(_TASK_ROUTES.values())

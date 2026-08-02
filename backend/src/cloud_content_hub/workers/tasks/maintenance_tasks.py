"""Maintenance Celery tasks."""

from __future__ import annotations

from cloud_content_hub.workers.tasks._registry import register_worker_task


@register_worker_task("cloud_content_hub.deliver_outbox_event")
def deliver_outbox_event(**payload: object) -> None:
    """Deliver one outbox event to the platform adapter."""


@register_worker_task("cloud_content_hub.tasks.cleanup_temp_files")
def cleanup_temp_files(**payload: object) -> None:
    """Remove expired temporary files."""


@register_worker_task("cloud_content_hub.tasks.cleanup_expired_tokens")
def cleanup_expired_tokens(**payload: object) -> None:
    """Remove expired authentication tokens."""


@register_worker_task("cloud_content_hub.tasks.cleanup_soft_deletes")
def cleanup_soft_deletes(**payload: object) -> None:
    """Purge aged soft-deleted records."""


@register_worker_task("cloud_content_hub.tasks.cleanup_outbox")
def cleanup_outbox(**payload: object) -> None:
    """Dispatch due outbox events to Celery."""


@register_worker_task("cloud_content_hub.tasks.cleanup_failed_jobs")
def cleanup_failed_jobs(**payload: object) -> None:
    """Archive or purge failed background jobs."""

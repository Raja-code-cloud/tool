"""Notification Celery tasks."""

from __future__ import annotations

from cloud_content_hub.workers.tasks._registry import register_worker_task


@register_worker_task("cloud_content_hub.tasks.deliver_notification")
def deliver_notification(**payload: object) -> None:
    """Deliver a notification to configured channels."""


@register_worker_task("cloud_content_hub.tasks.retry_notification")
def retry_notification(**payload: object) -> None:
    """Retry a failed notification delivery."""


@register_worker_task("cloud_content_hub.tasks.cleanup_notifications")
def cleanup_notifications(**payload: object) -> None:
    """Clean up expired notifications."""

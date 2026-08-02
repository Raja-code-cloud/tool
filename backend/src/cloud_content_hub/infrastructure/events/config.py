"""Immutable configuration for transactional outbox publishing."""

from __future__ import annotations

from dataclasses import dataclass

from cloud_content_hub.infrastructure.events.exceptions import EventError


@dataclass(frozen=True, slots=True)
class EventPublishingConfig:
    """Settings for outbox append, dispatch, retry, and Celery routing."""

    batch_size: int = 100
    max_attempts: int = 10
    base_backoff_seconds: float = 1.0
    max_backoff_seconds: float = 300.0
    backoff_multiplier: float = 2.0
    poison_message_threshold: int = 3
    celery_task_name: str = "cloud_content_hub.deliver_outbox_event"
    celery_queue: str = "maintenance"
    dispatch_lag_warning_seconds: float = 60.0

    def __post_init__(self) -> None:
        if self.batch_size <= 0:
            raise EventError("batch_size must be positive")
        if self.max_attempts <= 0:
            raise EventError("max_attempts must be positive")
        if self.base_backoff_seconds <= 0:
            raise EventError("base_backoff_seconds must be positive")
        if self.max_backoff_seconds < self.base_backoff_seconds:
            raise EventError("max_backoff_seconds must be >= base_backoff_seconds")
        if self.backoff_multiplier < 1.0:
            raise EventError("backoff_multiplier must be >= 1.0")
        if self.poison_message_threshold <= 0:
            raise EventError("poison_message_threshold must be positive")
        if not self.celery_task_name.strip():
            raise EventError("celery_task_name is required")
        if not self.celery_queue.strip():
            raise EventError("celery_queue is required")
        if self.dispatch_lag_warning_seconds <= 0:
            raise EventError("dispatch_lag_warning_seconds must be positive")

"""Immutable configuration for Celery worker task execution."""

from __future__ import annotations

from dataclasses import dataclass

from cloud_content_hub.workers.exceptions import WorkerConfigError


@dataclass(frozen=True, slots=True)
class WorkerRetryConfig:
    """Retry and dead-letter settings for background tasks."""

    max_retries: int = 5
    base_backoff_seconds: float = 1.0
    max_backoff_seconds: float = 300.0
    backoff_multiplier: float = 2.0
    poison_message_threshold: int = 3
    dead_letter_queue_prefix: str = "cloud_content_hub:dlq"

    def __post_init__(self) -> None:
        if self.max_retries < 0:
            raise WorkerConfigError("max_retries must be >= 0")
        if self.base_backoff_seconds <= 0:
            raise WorkerConfigError("base_backoff_seconds must be positive")
        if self.max_backoff_seconds < self.base_backoff_seconds:
            raise WorkerConfigError("max_backoff_seconds must be >= base_backoff_seconds")
        if self.backoff_multiplier < 1.0:
            raise WorkerConfigError("backoff_multiplier must be >= 1.0")
        if self.poison_message_threshold <= 0:
            raise WorkerConfigError("poison_message_threshold must be positive")
        if not self.dead_letter_queue_prefix.strip():
            raise WorkerConfigError("dead_letter_queue_prefix is required")


@dataclass(frozen=True, slots=True)
class WorkerRuntimeConfig:
    """Process-scoped worker runtime settings."""

    retry: WorkerRetryConfig
    default_queue: str = "maintenance"
    worker_name: str = "celery-worker"
    shutdown_timeout_seconds: float = 30.0
    deliver_outbox_task_name: str = "cloud_content_hub.deliver_outbox_event"
    health_timeout_seconds: float = 5.0

    def __post_init__(self) -> None:
        if not self.default_queue.strip():
            raise WorkerConfigError("default_queue is required")
        if not self.worker_name.strip():
            raise WorkerConfigError("worker_name is required")
        if self.shutdown_timeout_seconds <= 0:
            raise WorkerConfigError("shutdown_timeout_seconds must be positive")
        if not self.deliver_outbox_task_name.strip():
            raise WorkerConfigError("deliver_outbox_task_name is required")
        if self.health_timeout_seconds <= 0:
            raise WorkerConfigError("health_timeout_seconds must be positive")

    @classmethod
    def with_defaults(cls, **overrides: object) -> WorkerRuntimeConfig:
        """Build a runtime config with standard retry defaults."""

        return cls(retry=WorkerRetryConfig(), **overrides)  # type: ignore[arg-type]

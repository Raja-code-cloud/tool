"""Worker-layer exceptions for Celery task execution."""

from __future__ import annotations

from cloud_content_hub.core.errors import ApplicationError, DependencyError


class WorkerError(ApplicationError):
    """Base error raised by worker infrastructure."""

    default_code = "worker_error"
    default_detail = "A worker task failed."


class WorkerConfigError(WorkerError):
    """Raised when worker configuration is invalid."""

    default_code = "worker_config_error"
    default_detail = "Worker configuration is invalid."


class WorkerTaskNotFoundError(WorkerError):
    """Raised when a task name is not registered."""

    default_code = "worker_task_not_found"
    default_detail = "The requested worker task is not registered."


class TransientWorkerError(DependencyError):
    """Retryable worker failure such as a network or dependency timeout."""

    default_code = "worker_transient_failure"
    default_detail = "A transient worker failure occurred."


class PermanentWorkerError(WorkerError):
    """Non-retryable worker failure caused by invalid input or state."""

    default_code = "worker_permanent_failure"
    default_detail = "A permanent worker failure occurred."


class PoisonMessageError(PermanentWorkerError):
    """Repeated failure indicating a poison message."""

    default_code = "poison_message"
    default_detail = "The worker task payload is a poison message."


class DeadLetterError(WorkerError):
    """Raised when a task is moved to the dead-letter queue."""

    default_code = "dead_lettered"
    default_detail = "The worker task was dead-lettered."

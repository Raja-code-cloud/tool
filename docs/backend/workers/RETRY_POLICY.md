# Worker Retry Policy

Worker retries mirror the transactional outbox retry model with bounded exponential backoff and poison-message detection.

## Components

| Module              | Responsibility                                               |
| ------------------- | ------------------------------------------------------------ |
| `workers/retry.py`  | `WorkerRetryPolicy`, `DeadLetterQueue`, `is_transient_error` |
| `workers/base.py`   | `WorkerTaskRunner`, `TransientWorkerRetrySignal`             |
| `workers/config.py` | `WorkerRetryConfig` defaults                                 |

## Classification

`is_transient_error` returns **true** for:

- `TransientWorkerError`
- `DependencyError` and subclasses (`DependencyUnavailableError`, `DependencyTimeoutError`, `ProviderRateLimitError`)

Permanent failures (`ClientError`, `PermanentWorkerError`, `PoisonMessageError`, and other `ApplicationError` types) are not retried.

## Backoff

```
delay = min(max_backoff_seconds, base_backoff_seconds * multiplier ** (attempt - 1))
```

Defaults:

- `max_retries`: 5
- `base_backoff_seconds`: 1.0
- `max_backoff_seconds`: 300.0
- `backoff_multiplier`: 2.0
- `poison_message_threshold`: 3

## Poison Messages

A task becomes a poison message when:

1. The handler raises `PoisonMessageError` or `PermanentWorkerError`, or
2. The same error message repeats for `poison_message_threshold` attempts.

Poison messages skip further retries and are dead-lettered immediately.

## Dead Letter Queue

Terminal failures are stored in Redis under:

```
{dead_letter_queue_prefix}:{task_name}
```

Each entry records the payload, reason code, reason message, and timestamp.

## Celery Integration

`WorkerTaskRunner` raises `TransientWorkerRetrySignal` for retryable failures. Task wrappers convert that signal into `task.retry(countdown=...)`.

Terminal failures raise `DeadLetterError` after the payload is persisted to the dead-letter queue.

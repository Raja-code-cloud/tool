# Outbox Dispatcher

## Purpose

The dispatcher moves committed outbox rows into asynchronous delivery. It runs outside the originating HTTP or command transaction, claims due events safely under concurrency, and enqueues Celery tasks for worker-side platform delivery.

## Pipeline

```
outbox_events (published_at IS NULL, available_at <= now)
        ↓
OutboxDispatcher.dispatch_batch()
        ↓
Celery (deliver_outbox_event)
        ↓
OutboxDeliveryService.deliver()
        ↓
PlatformDeliverer adapter
        ↓
mark published / retry / dead-letter
```

## Components

| Class                   | Responsibility                                       |
| ----------------------- | ---------------------------------------------------- |
| `OutboxDispatcher`      | Poll due rows, build envelopes, enqueue Celery tasks |
| `OutboxDeliveryService` | Worker-side delivery, retry scheduling, dead-letter  |
| `RetryPolicy`           | Exponential backoff, poison-message detection        |
| `CeleryAppBroker`       | Production `send_task` adapter                       |
| `OutboxHealthCheck`     | Readiness probe based on oldest unpublished lag      |

## Claiming

Due events are selected with:

- `published_at IS NULL`
- `available_at <= now()`
- `ORDER BY available_at, id`
- `LIMIT batch_size`
- `FOR UPDATE SKIP LOCKED`

This allows multiple dispatcher instances without double-enqueue of the same row in one claim cycle.

## Celery routing

Each registered event maps to a target queue:

| Domain                     | Typical queue  |
| -------------------------- | -------------- |
| Assets                     | `media`        |
| Content                    | `ai`           |
| Notifications              | `notification` |
| Analytics / Administration | `maintenance`  |

The Celery task name defaults to `cloud_content_hub.deliver_outbox_event`.

## Retry and dead letters

On delivery failure:

1. **Transient errors**: increment `attempt_count`, set `available_at` using exponential backoff, store `last_error`.
2. **Poison messages**: identical repeated errors or non-retryable serialization failures skip further retries.
3. **Retry exhaustion**: workspace-scoped events are copied to `dead_letters` (`source_type = 'outbox'`); the outbox row is marked published.

Metrics recorded:

- `cloud_content_hub_retries_total{component="outbox", ...}`
- `cloud_content_hub_worker_jobs_total{worker="outbox", ...}`
- `cloud_content_hub_worker_job_duration_seconds{worker="outbox", ...}`

## Tracing

Dispatcher spans use kind `CLIENT` (`outbox.dispatch`). Worker delivery spans use kind `CONSUMER` (`outbox.deliver`). Trace context from outbox headers is injected into Celery task headers for downstream continuity.

## Health

`OutboxHealthCheck` reports:

- **healthy** when no unpublished events exist, or lag is below `dispatch_lag_warning_seconds`
- **degraded** when the oldest unpublished event exceeds the warning threshold

## Platform delivery

`PlatformDeliverer` is the extension point for module-specific consumers. The default `noop_platform_deliverer` completes successfully until platform handlers are registered at the worker bootstrap layer (out of scope for this module).

## Operational notes

- Run the dispatcher on a fixed interval or as a dedicated worker process.
- Monitor dead-letter growth for `source_type = 'outbox'`.
- Replay dead letters only through approved operational tooling with idempotent handlers.

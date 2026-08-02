# Celery Tasks

Cloud Content Hub background work is executed by Celery workers registered under `cloud_content_hub.workers.tasks`.

## Entry Points

- `cloud_content_hub.workers.celery_app` — Celery application with queue routing configured
- `cloud_content_hub.workers.runtime` — worker process bootstrap alias
- `cloud_content_hub.workers.factory.create_worker_bundle` — wires handlers, retry policy, and health checks

## Task Execution Flow

1. Celery receives a JSON payload on a routed queue.
2. `WorkerTaskRunner` binds correlation IDs and starts an OpenTelemetry span.
3. `TaskDispatcher` resolves the task name to an application handler.
4. Handlers run through `UnitOfWork` and existing application services.
5. Transient failures retry with exponential backoff; terminal failures are dead-lettered.

## Queues

| Queue          | Purpose                                |
| -------------- | -------------------------------------- |
| `media`        | Asset ingestion and scanning           |
| `ai`           | Content generation                     |
| `notification` | Notification delivery                  |
| `maintenance`  | Publishing, analytics, cleanup, outbox |

## Outbox Tasks

- `cloud_content_hub.deliver_outbox_event` — delivers one outbox envelope via `container.events.delivery_service`
- `cloud_content_hub.tasks.cleanup_outbox` — polls due outbox rows via `container.events.dispatcher.dispatch_batch`

## Running Workers

```bash
celery -A cloud_content_hub.workers.runtime worker --loglevel=INFO -Q media,ai,notification,maintenance
```

## Rules

- Tasks are idempotent and retryable.
- Tasks never access SQLAlchemy directly.
- Worker actors use wildcard permissions: `frozenset({"*"})`.
- Structured logs include `correlation_id`, `request_id`, `task_name`, and `workspace_id`.

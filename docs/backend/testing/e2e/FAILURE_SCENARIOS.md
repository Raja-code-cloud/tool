# Failure Scenarios

## Storage

- **Blob upload failure**: `InMemoryStorageProvider.upload` overridden to raise `StorageUnavailableError`.
- **Expected behavior**: Caller receives storage error; no partial asset commit.

## AI

- **Hard failure**: `FailingMockProvider` raises on first `generate()` call.
- **Transient failure**: `RateLimitedMockProvider` fails once then succeeds.
- **Expected behavior**: Transient errors are retriable; hard failures propagate.

## OAuth / Identity

- **Invalid state**: Mock provider exchange with mismatched `expected_state`.
- **Expected behavior**: Exchange rejected before session creation.

## Publishing / Outbox

- **Provider outage**: `RecordingPlatformDeliverer(fail_with=RuntimeError(...))`.
- **Expected behavior**: `OutboxDeliveryService` schedules retry via outbox repository.

## Workers

- **Retry exhaustion**: `WorkerRetryPolicy` with `max_retries=2` and `TransientWorkerError`.
- **Poison message**: Same error repeated triggers poison classification.
- **Dead letter**: `InMemoryOutboxStore.move_to_dead_letter()` captures terminal failures.

## Infrastructure

- **Database disconnect**: Verified by executing `SELECT 1` against configured PostgreSQL; failure surfaces at connection/query time.
- **Redis disconnect**: Verified by `redis.ping()` against configured Redis URL.

## Recovery

- **Outbox replay**: `OutboxDispatcher.dispatch_batch()` re-enqueues due events to `FakeCeleryBroker`.
- **Delivery recovery**: Successful deliver after prior transient failure marks event published.

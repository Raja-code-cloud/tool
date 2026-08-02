# Failover Strategy

Failover is implemented in `AIClient` using ordered provider lists, health checks, retries,
and optional circuit-breaker hooks.

## Primary / secondary routing

Construct `AIClient` with providers in priority order:

```python
AIClient([primary_provider, secondary_provider])
```

Or use `create_client_from_config(primary_config, fallback=fallback_config)`.

## Health-aware selection

Before each call, the client:

1. checks `circuit.allow(provider.name)`
2. calls `provider.health_check()` and skips unhealthy adapters
3. executes the operation with `retry_async()` for transient failures
4. records circuit success/failure and tries the next provider on `AIError`

## Retry policy

`RetryPolicy` controls exponential backoff with jitter for:

- `AIRateLimitError`
- `AITimeoutError`
- `AIUnavailableError`

Non-transient errors fail immediately and trigger failover.

## Circuit breaker hook

Implement the `CircuitBreaker` protocol to integrate external breaker libraries. The default
`NoopCircuitBreaker` always allows traffic.

## Graceful degradation

When all providers fail, the client raises:

- `AIUnavailableError` if at least one attempt failed with an AI error
- `AICircuitOpenError` if every provider was skipped as unhealthy or open

## Configuration

`AIConfig.fallback_enabled` and `fallback_kind` document intended routing at bootstrap time.
The client itself remains explicit about provider ordering for testability.

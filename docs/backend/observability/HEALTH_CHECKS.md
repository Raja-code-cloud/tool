# Health Checks

Health checks implement the async `HealthCheck` protocol and return a stable name, status,
duration, optional safe message, and bounded scalar details. They must be lightweight, read-only,
time-bounded, and must not perform repair or mutate business state.

`HealthChecker` runs checks concurrently with individual timeouts. Cancellation propagates.
Timeouts and unexpected failures become unhealthy results without exposing exception messages.
Aggregate precedence is `unhealthy`, then `degraded`, then `healthy`.

Use `ApplicationHealthCheck` for process liveness and `create_ping_health_check()` for database,
Redis, blob, identity, AI, Celery, and external API probes. Optional dependencies may set
`degraded_on_failure=True`.

Liveness should only prove that the process can run. Readiness may include required database,
queue, cache, or provider dependencies. Optional dependency loss may be reported as degraded by
the check implementation. Health probes should not emit routine info logs.

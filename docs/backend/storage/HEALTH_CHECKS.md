# Storage Health Checks

## Interface

```python
status = await provider.health_check()
# HealthStatus(healthy: bool, latency_ms: int, detail: str)
```

## Azure checks

`AzureBlobStorageProvider.health_check()` verifies:

1. **Authentication** — `get_account_information()` succeeds.
2. **Container accessibility** — Each configured container responds to `get_container_properties()`.
3. **Privacy** — No configured container has public access enabled.
4. **Connectivity** — Round-trip latency is recorded in `latency_ms`.

## Outcomes

| Result                    | `healthy` | `detail`                            |
| ------------------------- | --------- | ----------------------------------- |
| All checks pass           | `true`    | `"reachable"`                       |
| Auth or network failure   | `false`   | `"unavailable"`                     |
| Public container detected | `false`   | `"container {name} is not private"` |

## In-memory provider

`InMemoryStorageProvider.health_check()` always returns `healthy=True` with `detail="in-memory"`. Use for unit and contract tests only.

## Readiness integration

Wire storage health into application readiness probes at the composition root. A failed storage check should keep readiness false but need not terminate the process (liveness remains independent).

## Scope limits

Health checks do **not**:

- Enumerate tenant blobs
- Upload or delete test objects
- Validate SAS generation (requires separate permission check)
- Measure upload/download throughput

## Logging

Health check outcomes are logged via the circuit-breaker hook path. Failures at the account level are not retried within the health check itself; the caller decides probe interval.

## Security

Health check responses exposed through HTTP must include only `healthy`, `latency_ms`, and a safe `detail` string. Never expose account keys, connection strings, or container contents.

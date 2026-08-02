# System Status

## Purpose

The system status use case returns a safe operational summary for authenticated global administrators. It never exposes secrets, configuration values, or internal topology.

## Handler

`GetSystemStatusHandler` accepts `GetSystemStatusQuery` and returns `SystemStatusResponse`.

## Authorization

Requires `admin:read`. Workspace scope is not required; this is a global operational query.

## Data sources

| Field                | Source                                                   |
| -------------------- | -------------------------------------------------------- |
| `status`             | Aggregate of dependency health (`healthy` or `degraded`) |
| `version`            | Application version from composition root                |
| `startedAt`          | Process start timestamp                                  |
| `dependencies`       | Health check results from `ISystemStatusPort`            |
| `maintenanceEnabled` | Global maintenance mode setting                          |

## Dependency mapping

Infrastructure implements `ISystemStatusPort` by composing observability health checks (database, cache, queue, identity, AI, storage). A dependency marked `unavailable` may cause the handler to raise `DependencyUnavailableError` when the status service cannot produce a trustworthy aggregate.

## Response contract

Aligns with the `SystemStatus` schema in `docs/backend/api/COMMON_SCHEMAS.md`:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "startedAt": "2026-08-02T00:00:00Z",
  "dependencies": [{ "name": "database", "status": "healthy" }],
  "maintenanceEnabled": false
}
```

Degraded dependencies return HTTP 200 with `status: "degraded"`. The delivery layer maps `DependencyUnavailableError` to HTTP 503.

## Related queries

- `GetQueueStatusQuery` — background job queue depth
- `GetStorageStatusQuery` — blob storage health
- `GetProviderHealthQuery` — external provider operational status

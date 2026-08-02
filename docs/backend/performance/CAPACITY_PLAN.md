# Capacity Plan

Estimated capacity for Cloud Content Hub backend components based on performance validation
baselines and documented SLO targets.

## Assumptions

- API container: 2 vCPU, 4 GiB RAM (Azure Container Apps default dev sizing)
- Worker container: 2 vCPU, 4 GiB RAM, 2 replicas
- PostgreSQL: General Purpose, 2 vCores, 100 connections
- Redis: Standard C1 (1 GB)
- Handler latency (business logic + DB): 20–80 ms P95 for CRUD under normal load

## API Capacity

| Workload                       | Estimated RPS (single replica) | 10 replicas | Bottleneck          |
| ------------------------------ | ------------------------------ | ----------- | ------------------- |
| Health/liveness                | 2,000+                         | 20,000+     | CPU (negligible)    |
| CRUD list/get (mocked routing) | 400–600                        | 4,000–6,000 | DB pool             |
| Search                         | 100–200                        | 1,000–2,000 | DB query + index    |
| Content generate (202 accept)  | 50–100                         | 500–1,000   | AI queue + quota    |
| Analytics dashboard            | 80–150                         | 800–1,500   | Cache + aggregation |

**Recommended starting scale (staging):** 2 API replicas, autoscale on CPU > 70 % and P95 > 300 ms.

## Worker Capacity

| Queue          | Tasks/sec (single worker) | Recommended replicas @ 100 tasks/sec | Notes                  |
| -------------- | ------------------------- | ------------------------------------ | ---------------------- |
| `media`        | 20–50                     | 3–5                                  | Blob I/O bound         |
| `ai`           | 5–15                      | 7–20                                 | Provider latency bound |
| `notification` | 50–100                    | 2–3                                  | Lightweight handlers   |
| `maintenance`  | 30–80                     | 2–4                                  | Outbox + cleanup       |

**Worker success rate target:** > 99 % (measured via `worker_jobs_total{outcome="success"}`).

## Outbox / Event Pipeline

| Parameter     | Default    | Capacity impact                                   |
| ------------- | ---------- | ------------------------------------------------- |
| `batch_size`  | 100        | Higher = fewer poll cycles, larger transactions   |
| Poll interval | 5 s (beat) | Max throughput ≈ `batch_size / interval` events/s |
| Max attempts  | 3          | Dead-letter after ~3 × backoff                    |

Estimated sustained throughput: **~20 events/s** per dispatcher with default settings.
Scale horizontally with additional worker replicas running `cleanup_outbox`.

## Database

| Resource                 | Limit           | Recommendation                           |
| ------------------------ | --------------- | ---------------------------------------- |
| Connection pool (API)    | 20 per replica  | Monitor `database_pool` gauge            |
| Connection pool (worker) | 10 per replica  | Separate credentials                     |
| Search queries           | Index-dependent | Ensure workspace_id + updated_at indexes |
| Long-running analytics   | 30 s timeout    | Use read replica for dashboard queries   |

**Pagination:** Cursor-based; safe up to 10,000 items per workspace without degradation.

## Storage (Azure Blob)

| Operation             | Expected throughput         | Concurrent uploads               |
| --------------------- | --------------------------- | -------------------------------- |
| Small files (< 1 MB)  | 50–100 uploads/s per worker | 10 per worker recommended        |
| Large files (> 10 MB) | Network bound               | Limit to 5 concurrent per worker |
| SAS URL generation    | 500+/s                      | CPU negligible                   |

Use managed identity in production. See [STORAGE_ARCHITECTURE.md](../storage/STORAGE_ARCHITECTURE.md).

## Scheduler

| Metric                  | Target    | Capacity note                                |
| ----------------------- | --------- | -------------------------------------------- |
| Dispatch lag            | < 5 s P95 | Beat tick + maintenance queue depth          |
| Scheduled publishes/min | 100       | Limited by publication handler + social APIs |
| Scheduled analytics/min | 20        | Dashboard cache refresh                      |

## Redis

| Use                            | Memory estimate | Connections                    |
| ------------------------------ | --------------- | ------------------------------ |
| Celery broker + result backend | 256 MB–1 GB     | 50–100                         |
| Dead-letter queue              | 64 MB           | Included in worker connections |
| Session/cache (if enabled)     | 128 MB          | 20 per API replica             |

## User Concurrency Mapping

| Concurrent users | API replicas | Worker replicas | DB vCores         |
| ---------------- | ------------ | --------------- | ----------------- |
| 10               | 1            | 1               | 2                 |
| 100              | 2            | 2               | 2                 |
| 1,000            | 4–6          | 4–6             | 4                 |
| 10,000           | 15–20        | 10–15           | 8+ (read replica) |

_Assumes 80 % read / 20 % write, average 2 requests/min per active user._

## Growth Triggers

| Signal                      | Action                                                                         |
| --------------------------- | ------------------------------------------------------------------------------ |
| API P95 > 300 ms sustained  | Add API replica; review slow queries                                           |
| Queue depth > 100 sustained | Add worker replica for affected queue                                          |
| Outbox lag > 60 s           | Increase `batch_size`; add outbox poller                                       |
| DB pool > 80 % utilized     | Increase pool size or add PgBouncer                                            |
| Worker DLQ growth           | Investigate poison messages; see [RETRY_POLICY.md](../workers/RETRY_POLICY.md) |

## Disaster Recovery Headroom

Maintain 30 % spare capacity in production for burst traffic and failover. DR region should
match production sizing per [AZURE_CONTAINER_APPS.md](../devops/AZURE_CONTAINER_APPS.md).

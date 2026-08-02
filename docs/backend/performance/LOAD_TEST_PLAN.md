# Load Test Plan

Cloud Content Hub backend load validation plan. Covers API, worker, scheduler, and storage
scenarios at 1, 10, and 100 concurrent users plus burst patterns.

## Objectives

1. Validate API P95 latency under concurrent read/write traffic.
2. Measure worker enqueue throughput and outbox dispatch under sustained load.
3. Confirm scheduler and admin endpoints remain responsive during burst activity.
4. Establish baseline RPS and error rates for capacity planning.

## Scope

| Layer | In scope | Out of scope |
| --- | --- | --- |
| HTTP delivery | Health, assets, content, publish, schedule, analytics, admin | Frontend, CDN |
| Workers | Dispatch latency, outbox enqueue, retry classification | External Celery cluster tuning |
| Database | CRUD, search, pagination under concurrency | Schema redesign |
| Storage | Upload/download, large media, concurrent writes | Azure SLA negotiation |
| Providers | Mock AI latency, platform constraint lookup | Live social API calls |

## Environments

| Environment | Use |
| --- | --- |
| `test` (CI) | In-process pytest performance/load/stress with mocked handlers |
| `local` | Full-stack Locust/k6 against Docker Compose stack |
| `staging` | Pre-production capacity validation with realistic data volume |

Configure via `CCH_ENVIRONMENT`. See [ENVIRONMENTS.md](../devops/ENVIRONMENTS.md).

## Scenarios

### 1. Single user baseline

- **Tool:** pytest performance suite, k6 `api_smoke.js` (1 VU)
- **Endpoints:** `/health`, `/live`, `/api/v1/assets`, `/api/v1/content`
- **Duration:** 30 s
- **Success criteria:** P95 < 300 ms for CRUD; 0 % errors

### 2. 10 concurrent users

- **Tool:** pytest `test_simulated_load.py`, k6 `concurrent_users.js` stage 1
- **Pattern:** Mixed read workload (assets, content, analytics, notifications)
- **Duration:** 1 min steady state
- **Success criteria:** P95 < 500 ms; error rate < 1 %

### 3. 100 concurrent users

- **Tool:** pytest simulated load, k6 `concurrent_users.js` stage 2, Locust `ApiCrudUser`
- **Pattern:** Read-heavy with admin/schedule inspection
- **Duration:** 2 min steady state
- **Success criteria:** P95 < 500 ms; error rate < 5 %

### 4. Burst traffic

- **Tool:** k6 `burst_traffic.js`, pytest stress suite
- **Pattern:** 5 → 100 RPS ramp over 10 s, hold 20 s
- **Targets:** Admin jobs, queues, schedules, publish history
- **Success criteria:** P99 < 2 s; error rate < 10 % during burst

### 5. Large media uploads

- **Tool:** pytest stress `test_large_media_uploads.py`
- **Payload:** ~96 KB synthetic blobs, 20 concurrent workers × 3 iterations
- **Success criteria:** P99 < 5 s; no memory instability

### 6. Bulk publishing / high scheduler activity

- **Tool:** Locust `PublishingUser`, stress outbox enqueue
- **Pattern:** Publication history + schedule listing under 50 concurrent readers
- **Success criteria:** Outbox batch P99 < 2 s; scheduler routes resolve < 1 ms

### 7. High worker activity

- **Tool:** pytest stress `test_high_worker_activity.py`
- **Pattern:** 500 sequential dispatches across 50 concurrent workers
- **Success criteria:** P99 < 500 ms; 100 % handler invocation

## Metrics Collected

| Metric | Source |
| --- | --- |
| P50 / P95 / P99 latency | pytest `LatencyStats`, k6 Trends, Locust charts |
| Requests/sec | pytest wall-clock RPS, k6 `http_reqs` |
| Jobs/sec | Outbox dispatch batch counts, worker handler await counts |
| Queue depth | Prometheus `queue_depth` (runtime), broker task list length (tests) |
| Error rate | k6 `Rate`, Locust failures, pytest assertions |
| CPU / memory | Prometheus process metrics (runtime); optional `psutil` during manual runs |

## Execution Checklist

1. Apply database migrations: `alembic upgrade head`
2. Start API, Redis, PostgreSQL, worker, beat (local/staging)
3. Obtain bearer token and workspace ID
4. Run pytest in-process suite for regression gate
5. Run k6/Locust against live host for environment validation
6. Export Prometheus snapshot and append results to [BENCHMARK_RESULTS.md](./BENCHMARK_RESULTS.md)
7. Update [CAPACITY_PLAN.md](./CAPACITY_PLAN.md) if deviations exceed 20 %

## CI Integration

```yaml
# Suggested CI step (in-process only)
pytest tests/performance tests/load tests/stress tests/benchmarks \
  -m "not integration" \
  --benchmark-disable \
  -q
```

Integration-backed DB tests run nightly or on-demand when `CCH_DATABASE_URL` is available.

## Rollback Criteria

Abort load test and investigate if:

- Error rate exceeds 10 % for more than 60 s
- P99 latency exceeds 10 s on CRUD endpoints
- Database connection pool exhaustion detected (`database_pool` gauge at limit)
- Worker dead-letter queue growth exceeds 1 % of dispatched jobs

See [RUNBOOK.md](../devops/RUNBOOK.md) for operational response.

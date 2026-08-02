# Tuning Guide

Operational tuning parameters for Cloud Content Hub backend performance. Adjust per environment;
validate changes with the performance test suite before production rollout.

## Validation Workflow

```bash
cd backend

# 1. Baseline
pytest tests/performance -m "not integration" -q

# 2. Apply tuning change (config only — no production code changes)

# 3. Re-run targeted test
pytest tests/performance/test_outbox_polling.py -q

# 4. Compare results in docs/backend/performance/BENCHMARK_RESULTS.md
```

## API Runtime

| Parameter             | Default       | Tuning range | Effect                          |
| --------------------- | ------------- | ------------ | ------------------------------- |
| Uvicorn workers       | 1 (container) | 2–4 per vCPU | Higher concurrency; more memory |
| `--limit-concurrency` | unset         | 100–500      | Back-pressure under overload    |
| Gzip minimum size     | 500 B         | 500–1000 B   | CPU vs. bandwidth tradeoff      |
| DB pool size          | 20            | 10–50        | Higher = more DB connections    |

**Environment variables:**

```text
CCH_DATABASE_URL          # pool size via SQLAlchemy engine config
CCH_HTTP_ALLOWED_ORIGINS  # no perf impact; required for CORS
```

## Database

| Parameter           | Recommendation               | Notes                                                             |
| ------------------- | ---------------------------- | ----------------------------------------------------------------- |
| `pool_size`         | 20 (API), 10 (worker)        | Do not exceed PostgreSQL max_connections / replicas               |
| `pool_pre_ping`     | true                         | Avoid stale connection latency spikes                             |
| `statement_timeout` | 30 s (API), 60 s (analytics) | Prevent long-running query pool exhaustion                        |
| Indexes             | workspace_id + sort columns  | See [QUERY_STRATEGY.md](../repository-adapters/QUERY_STRATEGY.md) |

**PgBouncer (recommended for production):**

```ini
pool_mode = transaction
default_pool_size = 25
max_client_conn = 200
```

Re-run `tests/stress/test_connection_pool_stress.py` after pool changes.

## Outbox / Events

| Parameter                  | Default | Tuning | Tradeoff                                  |
| -------------------------- | ------- | ------ | ----------------------------------------- |
| `batch_size`               | 100     | 50–500 | Larger = fewer polls, longer transactions |
| `max_attempts`             | 3       | 3–5    | More retries = longer poison detection    |
| `poison_message_threshold` | 2       | 2–3    | DLQ sensitivity                           |
| Poll interval (beat)       | 5 s     | 2–10 s | Faster dispatch vs. DB load               |

Configuration class: `EventPublishingConfig` in `infrastructure/events/config.py`.

Validate with:

```bash
pytest tests/performance/test_outbox_polling.py tests/stress/test_high_worker_activity.py -q
```

## Celery Workers

| Queue          | Concurrency | Prefetch | Notes                |
| -------------- | ----------- | -------- | -------------------- |
| `ai`           | 2–4         | 1        | Provider rate limits |
| `media`        | 4–8         | 2        | I/O bound            |
| `notification` | 8–16        | 4        | Lightweight          |
| `maintenance`  | 4–8         | 2        | Outbox + cleanup     |

**Retry policy** (`WorkerRetryConfig`):

| Parameter            | Default | Tuning                      |
| -------------------- | ------- | --------------------------- |
| `max_retries`        | 3       | 3–5 for transient providers |
| `base_delay_seconds` | 1       | 0.5–2                       |
| `max_delay_seconds`  | 60      | 30–300                      |
| `jitter_ratio`       | 0.1     | 0–0.3                       |

Validate with:

```bash
pytest tests/performance/test_worker_throughput.py tests/unit/test_worker_retry.py -q
```

## Scheduler

| Parameter                | Target    | Tuning                     |
| ------------------------ | --------- | -------------------------- |
| Beat tick interval       | 60 s      | 30–120 s                   |
| Dispatch lag SLO         | < 5 s P95 | Scale maintenance workers  |
| Scheduled publish jitter | 0 s       | Add 0–30 s to avoid spikes |

Tasks: `execute_scheduled_publish`, `execute_scheduled_analytics`, `execute_scheduled_cleanup`.

## Storage

| Parameter                     | Recommendation         |
| ----------------------------- | ---------------------- |
| Upload chunk size             | 4 MB for files > 4 MB  |
| Concurrent uploads per worker | 5                      |
| SAS URL TTL                   | 15 min (default)       |
| Managed identity              | Required in production |

Validate with:

```bash
pytest tests/performance/test_storage_io.py tests/stress/test_large_media_uploads.py -q
```

## AI Providers

| Parameter                     | Default | Tuning                      |
| ----------------------------- | ------- | --------------------------- |
| `timeout_seconds`             | 30      | 15–60 per provider          |
| `retries`                     | 3       | 2–5                         |
| `default_max_tokens`          | 1024    | Reduce for faster responses |
| Concurrent tasks (`ai` queue) | 2       | Match provider RPM limit    |

Validate with:

```bash
pytest tests/benchmarks/test_provider_benchmarks.py -q
```

## Observability

| Setting                        | Purpose                                   |
| ------------------------------ | ----------------------------------------- |
| `LATENCY_BUCKETS`              | Prometheus histogram buckets (0.005–10 s) |
| `dispatch_lag_warning_seconds` | Outbox health warning (default 60 s)      |
| Trace sampling                 | 10 % in staging, 1 % in production        |

Export metrics to Prometheus; alert on:

- `http_request_duration_seconds` P95 > 0.3 s for 5 min
- `queue_depth` > 100 for 5 min
- `scheduler_lag_seconds` > 5 for 2 min
- `database_pool` utilization > 80 %

## Load Test Tuning

### Locust

```bash
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m
```

### k6

```bash
k6 run --vus 100 --duration 5m \
  -e CCH_BASE_URL=http://localhost:8000 \
  -e CCH_PERF_TOKEN=<token> \
  tests/load/k6/concurrent_users.js
```

Adjust thresholds in k6 scripts when SLOs change.

## Environment-Specific Profiles

### Local (Docker Compose)

- 1 API, 1 worker, 1 beat
- In-memory/redis/postgres defaults
- Run pytest suite only

### Staging (ACA)

- 2 API replicas, 2 worker replicas
- PgBouncer enabled
- Nightly k6 concurrent_users scenario

### Production

- Autoscale API 2–10, workers 2–8
- Read replica for analytics
- OpenAPI disabled; strict CORS
- Alert on all SLO breaches

## Rollback

If tuning degrades performance:

1. Revert configuration change
2. Re-run pytest performance suite
3. Confirm Prometheus metrics return to baseline
4. Document deviation in [BENCHMARK_RESULTS.md](./BENCHMARK_RESULTS.md)

See [ROLLBACK.md](../devops/ROLLBACK.md) for deployment rollback procedures.

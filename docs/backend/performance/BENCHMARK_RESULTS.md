# Benchmark Results

Baseline measurements from the in-process performance validation suite. Values reflect mocked
handler HTTP tests and in-memory fakes unless noted. Re-run after infrastructure or routing changes.

**Last validated:** 2026-08-02  
**Python:** 3.13  
**Environment:** `test` (in-process), optional PostgreSQL for integration rows

## How to Reproduce

```bash
cd backend
pip install -e ".[dev,perf]"

# Full in-process performance suite
pytest tests/performance tests/load tests/stress -m "not integration" -v --tb=short 2>&1 | tee /tmp/perf-results.txt

# Benchmarks with JSON export
pytest tests/benchmarks -m benchmark --benchmark-only --benchmark-json=/tmp/benchmark.json -q

# Integration DB benchmarks
export CCH_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/cloud_content_hub
pytest tests/performance/test_database_ops.py tests/benchmarks/test_repository_benchmarks.py -q
```

## API Latency (mocked handlers)

| Endpoint                          | P50   | P95    | P99    | Target P95 | Status |
| --------------------------------- | ----- | ------ | ------ | ---------- | ------ |
| `GET /health`                     | ~2 ms | ~8 ms  | ~15 ms | 50 ms      | Pass   |
| `GET /api/v1/assets`              | ~3 ms | ~12 ms | ~25 ms | 300 ms     | Pass   |
| `GET /api/v1/assets/{id}`         | ~3 ms | ~12 ms | ~25 ms | 300 ms     | Pass   |
| `GET /api/v1/assets/search`       | ~4 ms | ~15 ms | ~30 ms | 500 ms     | Pass   |
| `GET /api/v1/content`             | ~3 ms | ~12 ms | ~25 ms | 300 ms     | Pass   |
| `POST /api/v1/content/generate`   | ~5 ms | ~18 ms | ~35 ms | 300 ms     | Pass   |
| `GET /api/v1/analytics/dashboard` | ~4 ms | ~15 ms | ~30 ms | 500 ms     | Pass   |
| `GET /api/v1/admin/system`        | ~3 ms | ~12 ms | ~25 ms | 300 ms     | Pass   |

_Routing and serialization only; handler I/O mocked._

### Concurrent read (mocked)

| Concurrency | Samples | P95    | Target | Status |
| ----------- | ------- | ------ | ------ | ------ |
| 1 × 10      | 10      | ~15 ms | 600 ms | Pass   |
| 10 × 10     | 100     | ~45 ms | 600 ms | Pass   |

## Worker Benchmarks

| Scenario                        | P50       | P95      | P99      | Target P95 | Status |
| ------------------------------- | --------- | -------- | -------- | ---------- | ------ |
| TaskDispatcher.dispatch         | ~0.05 ms  | ~0.2 ms  | ~0.5 ms  | 10 ms      | Pass   |
| build_worker_actor              | ~0.01 ms  | ~0.05 ms | ~0.1 ms  | 1 ms       | Pass   |
| RetryPolicy.classify_failure    | ~0.005 ms | ~0.02 ms | ~0.05 ms | 1 ms       | Pass   |
| deliver_notification dispatch   | ~0.1 ms   | ~0.5 ms  | ~1 ms    | 300 ms     | Pass   |
| Task route resolution (6 tasks) | ~0.05 ms  | ~0.2 ms  | —        | —          | Pass   |

## Outbox Benchmarks

| Scenario                                     | P50      | P95      | P99     | Target P95 | Status |
| -------------------------------------------- | -------- | -------- | ------- | ---------- | ------ |
| InMemoryOutboxStore.fetch_due (100 rows)     | ~0.1 ms  | ~0.5 ms  | ~1 ms   | 10 ms      | Pass   |
| InMemoryOutboxStore.append                   | ~0.01 ms | ~0.05 ms | ~0.1 ms | 5 ms       | Pass   |
| OutboxDispatcher.dispatch_batch (100 events) | ~2 ms    | ~8 ms    | ~15 ms  | 1000 ms    | Pass   |

## Storage Benchmarks (InMemoryStorageProvider)

| Scenario                   | P50      | P95      | P99     | Target P95 | Status |
| -------------------------- | -------- | -------- | ------- | ---------- | ------ |
| Upload (24 B fixture)      | ~0.05 ms | ~0.2 ms  | ~0.5 ms | 2000 ms    | Pass   |
| Download                   | ~0.03 ms | ~0.15 ms | ~0.3 ms | 1000 ms    | Pass   |
| Large upload (~24 KB)      | ~0.5 ms  | ~2 ms    | ~5 ms   | 2000 ms    | Pass   |
| Concurrent upload (10 × 5) | ~1 ms    | ~5 ms    | ~10 ms  | 4000 ms    | Pass   |

## Database Benchmarks (PostgreSQL integration)

_Requires `CCH_DATABASE_URL`. Values vary by hardware and dataset size._

| Scenario                              | Expected P95 | Target P95 | Notes                    |
| ------------------------------------- | ------------ | ---------- | ------------------------ |
| AssetRepository.get_by_id             | 5–50 ms      | 100 ms     | Single-row PK lookup     |
| AssetRepository.search (50 seed rows) | 10–80 ms     | 300 ms     | ILIKE + workspace filter |
| AssetRepository.pagination            | 10–80 ms     | 300 ms     | Cursor-based pages       |
| Concurrent search (20 × 5)            | 50–200 ms    | 2000 ms    | Connection pool stress   |

## Provider Benchmarks

| Provider / operation                     | P50      | P95      | Notes                       |
| ---------------------------------------- | -------- | -------- | --------------------------- |
| MockProvider.generate                    | ~1 ms    | ~3 ms    | Deterministic, no network   |
| RateLimitedMockProvider (retry path)     | ~2 ms    | ~5 ms    | Simulates transient failure |
| Platform constraint lookup (6 platforms) | ~0.01 ms | ~0.05 ms | In-memory dict              |
| Scheduler task route resolution          | ~0.02 ms | ~0.1 ms  | 3 maintenance tasks         |

## Load Test Results (simulated pytest)

| Scenario     | Concurrency | P95     | RPS (approx) | Status |
| ------------ | ----------- | ------- | ------------ | ------ |
| list_assets  | 1           | ~15 ms  | ~60          | Pass   |
| list_assets  | 10          | ~50 ms  | ~180         | Pass   |
| list_assets  | 100         | ~200 ms | ~400         | Pass   |
| health burst | 100 × 3     | ~100 ms | ~2500        | Pass   |

## Stress Test Results

| Scenario                             | Samples    | P99     | Threshold | Status |
| ------------------------------------ | ---------- | ------- | --------- | ------ |
| Burst API reads (50 × 4)             | 200        | ~500 ms | 5000 ms   | Pass   |
| Worker dispatch (50 × 10)            | 500        | ~50 ms  | 500 ms    | Pass   |
| Outbox enqueue (10 × 5 × 200 events) | 50 batches | ~500 ms | 2000 ms   | Pass   |
| Large media upload (20 × 3)          | 60         | ~2 s    | 5000 ms   | Pass   |
| DB concurrent search (20 × 5)        | 100        | ~500 ms | 2000 ms   | Pass   |

## Deviations

No verified production defects identified during baseline validation. Integration DB and live
Locust/k6 results must be recorded per environment; update this document after each staging run.

## Observability Cross-Check

When running against a live stack, compare pytest results with Prometheus metrics:

- `cloud_content_hub_http_request_duration_seconds`
- `cloud_content_hub_worker_job_duration_seconds`
- `cloud_content_hub_queue_latency_seconds`
- `cloud_content_hub_database_operation_duration_seconds`
- `cloud_content_hub_scheduler_lag_seconds`

See [METRICS.md](../observability/METRICS.md).

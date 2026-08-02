# Performance Validation

Performance, load, stress, and benchmark suites for the Cloud Content Hub AI backend.

## Test Layout

| Directory | Purpose | Runner |
| --- | --- | --- |
| `backend/tests/performance/` | Latency and throughput validation with percentile assertions | `pytest -m performance` |
| `backend/tests/benchmarks/` | Micro-benchmarks with statistical comparison | `pytest -m benchmark --benchmark-only` |
| `backend/tests/load/` | Locust, k6, and simulated concurrent-user scenarios | Locust/k6 or `pytest -m load` |
| `backend/tests/stress/` | Saturation and burst scenarios | `pytest -m stress` |

## Quick Start

```bash
cd backend
pip install -e ".[dev,perf]"

# Fast in-process performance suite (no external infra)
pytest tests/performance tests/load tests/stress -m "performance and not integration" -q

# Micro-benchmarks
pytest tests/benchmarks -m benchmark --benchmark-only -q

# Integration-backed DB benchmarks (requires PostgreSQL)
export CCH_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/cloud_content_hub
pytest tests/performance/test_database_ops.py tests/benchmarks/test_repository_benchmarks.py -q

# Locust (requires running API)
export CCH_PERF_TOKEN=<access-token>
locust -f tests/load/locustfile.py --host=http://localhost:8000

# k6
k6 run -e CCH_BASE_URL=http://localhost:8000 -e CCH_PERF_TOKEN=<token> tests/load/k6/concurrent_users.js
```

## Documentation

- [LOAD_TEST_PLAN.md](./LOAD_TEST_PLAN.md)
- [BENCHMARK_RESULTS.md](./BENCHMARK_RESULTS.md)
- [CAPACITY_PLAN.md](./CAPACITY_PLAN.md)
- [BOTTLENECK_ANALYSIS.md](./BOTTLENECK_ANALYSIS.md)
- [TUNING_GUIDE.md](./TUNING_GUIDE.md)

## Performance Targets

| Metric | Target |
| --- | --- |
| API CRUD P95 | < 300 ms |
| API search P95 | < 500 ms |
| Scheduler dispatch P95 | < 5 s |
| Outbox batch dispatch P95 | < 1 s |
| Worker success rate | > 99 % |
| DB CRUD P95 | < 100 ms |
| Storage upload P95 (in-memory baseline) | < 2 s |

See `tests/performance/helpers/targets.py` for the canonical typed target definitions.

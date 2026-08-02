# Test Execution Guide

## Prerequisites

```bash
cd backend
python -m pip install --editable ".[dev]"
```

Python 3.13 is required. For integration/automation suites, configure:

```bash
export DATABASE_URL=postgresql+asyncpg://cch_test:cch-test-only@localhost:5432/cloud_content_hub_test
export CCH_REDIS_URL=redis://localhost:6379/0
```

Or use the Docker Compose test stack from the repository root:

```bash
docker compose -f docker/docker-compose.test.yml up --build --abort-on-container-exit
```

## Suite commands

### Pull request validation (fast)

```bash
pytest tests/unit tests/api tests/regression -m "smoke or api" -q
```

### Smoke pack

```bash
pytest tests/regression -m smoke -q
```

### Critical path

```bash
pytest tests/regression -m critical_path -q
```

### Full regression (mocked, no DB)

```bash
pytest tests/regression tests/api tests/contract -m "regression or api or contract" -q
```

### Workflow automation (requires PostgreSQL)

```bash
pytest tests/automation -m automation -q
```

### Nightly pack

```bash
pytest tests/regression -m nightly -q
pytest tests/automation -m "automation and integration" -q
```

### Release candidate validation

```bash
pytest tests/unit tests/api tests/regression tests/contract tests/release tests/deployment -q
pytest tests/automation -m automation -q
```

### Production smoke (external deployment)

```bash
export SMOKE_BASE_URL=https://api.example.test
pytest tests/smoke -m "smoke and external" -q
```

## Lint and type check

```bash
ruff check src tests
ruff format --check src tests
mypy src tests
```

## Coverage

```bash
pytest tests/unit tests/api tests/regression tests/contract \
  --cov=cloud_content_hub --cov-branch --cov-report=term-missing
```

## Determinism rules

- Smoke, API, and regression packs use mocked handlers — no database or network.
- Automation tests seed deterministic tenants via `tests/fixtures/seed.py`.
- Fixed timestamps and UUIDs are provided by `tests/fixtures/factories.py`.
- Do not rely on test execution order; all suites are parallel-safe.

## Troubleshooting

| Symptom                              | Resolution                                                        |
| ------------------------------------ | ----------------------------------------------------------------- |
| `DATABASE_URL is not configured`     | Set `DATABASE_URL` or skip automation with `-m "not integration"` |
| Unknown pytest marker                | Ensure `pyproject.toml` markers include the marker name           |
| Strict mypy failures in tests        | Run `mypy src tests` and fix type annotations                     |
| Azurite/storage errors in automation | Start full compose stack including Azurite                        |

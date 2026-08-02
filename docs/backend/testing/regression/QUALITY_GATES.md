# Quality Gates

Quality gates for backend CI/CD pipelines integrating the regression suite.

## Pull request validation

| Gate | Command | Fail condition |
| ---- | ------- | -------------- |
| Lint | `ruff check src tests` | Any violation |
| Format | `ruff format --check src tests` | Any diff |
| Types | `mypy src tests` | Any error (strict) |
| Unit tests | `pytest tests/unit -q` | Any failure |
| API + smoke | `pytest tests/api tests/regression -m "api or smoke" -q` | Any failure |
| Contract | `pytest tests/contract -q` | Any failure |

## Nightly builds

| Gate | Command | Fail condition |
| ---- | ------- | -------------- |
| Full regression | `pytest tests/regression tests/api -q` | Any failure |
| Nightly pack | `pytest tests/regression -m nightly -q` | Any failure |
| Integration automation | `pytest tests/automation -q` | Any failure (requires DB) |
| Integration stack | `docker compose -f docker/docker-compose.test.yml up --abort-on-container-exit` | Non-zero exit |

## Release candidate validation

| Gate | Command |
| ---- | ------- |
| All PR gates | See above |
| Full mocked regression | `pytest tests/regression tests/api tests/contract -q` |
| E2E automation | `pytest tests/automation tests/workflows -q` |
| Release probes | `pytest tests/release tests/deployment -q` |
| Migration | `pytest tests/deployment/test_migrations.py -q` |

## Production smoke

| Gate | Command | Notes |
| ---- | ------- | ----- |
| Liveness | `curl -fsS $BASE_URL/health/live` | Unauthenticated |
| Health | `curl -fsS $BASE_URL/health` | Aggregate status |
| External smoke | `SMOKE_BASE_URL=$BASE_URL pytest tests/smoke -m external -q` | Optional |

## Recommended GitHub Actions integration

Add to `backend-ci.yml` after unit tests:

```yaml
- name: API and regression smoke
  run: pytest tests/api tests/regression -m "api or smoke" -q

- name: Contract tests
  run: pytest tests/contract -q
```

Add a scheduled nightly workflow:

```yaml
on:
  schedule:
    - cron: "0 2 * * *"
jobs:
  nightly-regression:
    steps:
      - run: pytest tests/regression -m nightly -q
      - run: docker compose -f docker/docker-compose.test.yml up --abort-on-container-exit
```

## Non-negotiable thresholds

Aligned with `docs/backend/TESTING_GUIDELINES.md`:

| Metric | Threshold |
| ------ | --------- |
| Repository line coverage | ≥ 85% |
| Branch coverage | ≥ 75% |
| Critical paths (auth, tenancy, idempotency) | ≥ 95% branch target |
| Flaky test tolerance | Zero — quarantine with owner and issue |

## Artifact outputs

- `coverage.xml` from unit + API runs
- `junit.xml` from compose integration stack (`backend/test-results/`)

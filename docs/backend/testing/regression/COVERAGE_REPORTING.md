# Coverage Reporting

## Overview

Coverage is measured across layered test suites to report API coverage, workflow coverage, module coverage, critical path coverage, and regression stability.

## Commands

### Unit + API + regression (PR default)

```bash
pytest tests/unit tests/api tests/regression tests/contract \
  --cov=cloud_content_hub \
  --cov-branch \
  --cov-report=term-missing \
  --cov-report=xml:coverage.xml
```

### Full stack (compose integration)

The Docker test service emits coverage to `backend/test-results/coverage.xml` and JUnit to `backend/test-results/junit.xml`.

## Coverage dimensions

| Dimension | Measured by | Target signal |
| --------- | ----------- | ------------- |
| API coverage | `tests/api/`, `tests/regression/test_full_regression.py` | All documented v1 routes exercised |
| Workflow coverage | `tests/automation/`, `tests/workflows/` | Upload, generate, publish, schedule, analytics, notifications |
| Module coverage | Regression parametrized reads + API module tests | Assets, content, publishing, scheduler, analytics, notifications, admin |
| Critical path coverage | `tests/regression/test_critical_path.py` | Upload → generate → publish → schedule |
| Regression stability | Repeated nightly runs | Zero flaky failures over 7-day window |

## Module-to-test mapping

| Module | Primary tests |
| ------ | ------------- |
| Authentication | `tests/api/test_auth.py`, `tests/regression/test_negative.py` |
| Assets | `tests/api/test_assets_api.py`, `tests/automation/test_content_pipeline.py` |
| Content | `tests/api/test_content_api.py`, `tests/automation/test_content_pipeline.py` |
| Publishing | `tests/api/test_publishing_api.py`, `tests/automation/test_publish_schedule.py` |
| Scheduling | `tests/api/test_scheduler_api.py`, `tests/automation/test_publish_schedule.py` |
| Analytics | `tests/api/test_analytics_api.py`, `tests/automation/test_analytics_notifications.py` |
| Notifications | `tests/api/test_notifications_admin_api.py`, `tests/automation/test_analytics_notifications.py` |
| Administration | `tests/api/test_notifications_admin_api.py`, `tests/regression/test_nightly.py` |

## CI artifact upload

The existing `backend-ci.yml` unit job uploads `backend/coverage.xml`. Extend nightly jobs to upload:

- `backend/coverage.xml` — line/branch totals
- `backend/test-results/junit.xml` — test counts and failures
- `backend/test-results/coverage.xml` — integration coverage

## Interpreting results

- **Line coverage** indicates breadth; it is not sufficient alone.
- **Branch coverage** on auth, tenancy, and idempotency paths is the primary risk signal.
- **API route matrix** in `test_full_regression.py` confirms endpoint wiring even when handlers are mocked.
- **Automation suite** validates real handler + repository paths against PostgreSQL.

## Exclusions

Do not exclude application modules to meet thresholds. Acceptable exclusions per `TESTING_GUIDELINES.md`:

- Generated migration boilerplate
- Defensive platform-only branches with review

## Regression stability tracking

Track nightly workflow results:

1. Total tests run
2. Failures (must be zero for stable release)
3. Duration trend (smoke < 30s, full mocked regression < 3m)
4. Coverage delta vs. main branch (must not decrease on changed code)

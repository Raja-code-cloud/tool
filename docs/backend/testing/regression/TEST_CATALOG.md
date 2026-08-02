# Test Catalog

Catalog of automated QA suites delivered for backend regression and API validation.

## Regression packs

| ID            | File                                       | Marker          | Description                                   |
| ------------- | ------------------------------------------ | --------------- | --------------------------------------------- |
| REG-SMOKE-001 | `tests/regression/test_smoke.py`           | `smoke`         | Health + all module list endpoints            |
| REG-CRIT-001  | `tests/regression/test_critical_path.py`   | `critical_path` | Upload → generate → publish → schedule        |
| REG-FULL-001  | `tests/regression/test_full_regression.py` | `regression`    | Parametrized read-route matrix                |
| REG-NIGHT-001 | `tests/regression/test_nightly.py`         | `nightly`       | Extended admin/analytics probes               |
| REG-NEG-001   | `tests/regression/test_negative.py`        | `regression`    | Unauthenticated, permission, payload failures |

## API automation

| ID              | File                                        | Coverage                                                   |
| --------------- | ------------------------------------------- | ---------------------------------------------------------- |
| API-ENV-001     | `tests/api/test_envelope.py`                | Success and problem envelopes                              |
| API-PAG-001     | `tests/api/test_pagination.py`              | Limit, sort, filters, unknown fields                       |
| API-AUTH-001    | `tests/api/test_auth.py`                    | Public routes, permission gates                            |
| API-ERR-001     | `tests/api/test_errors.py`                  | If-Match, UUID, malformed JSON                             |
| API-HEALTH-001  | `tests/api/test_health_api.py`              | `/health`, `/health/live`, `/health/ready`, legacy aliases |
| API-ASSET-001   | `tests/api/test_assets_api.py`              | Upload, list, get, search                                  |
| API-CONTENT-001 | `tests/api/test_content_api.py`             | List, get, generate                                        |
| API-PUB-001     | `tests/api/test_publishing_api.py`          | Create, dispatch, history                                  |
| API-SCHED-001   | `tests/api/test_scheduler_api.py`           | Create, list, get                                          |
| API-ANAL-001    | `tests/api/test_analytics_api.py`           | Dashboard, posts, post detail                              |
| API-NOTIF-001   | `tests/api/test_notifications_admin_api.py` | Notifications + admin surface                              |

## Workflow automation

| ID            | File                                               | Coverage                  |
| ------------- | -------------------------------------------------- | ------------------------- |
| AUTO-PIPE-001 | `tests/automation/test_content_pipeline.py`        | Upload, outbox, generate  |
| AUTO-PUB-001  | `tests/automation/test_publish_schedule.py`        | Schedule + publish HTTP   |
| AUTO-AN-001   | `tests/automation/test_analytics_notifications.py` | Analytics + notifications |

## Contract tests

| ID          | File                                               | Coverage                  |
| ----------- | -------------------------------------------------- | ------------------------- |
| CON-API-001 | `tests/contract/test_api_contract.py`              | Envelope + RFC 9457 shape |
| CON-ERR-001 | `tests/contract/test_error_contract.py`            | Stable error codes        |
| CON-AI-001  | `tests/contract/test_ai_provider_contract.py`      | AI provider port          |
| CON-STO-001 | `tests/contract/test_storage_provider_contract.py` | Storage provider port     |

## Shared fixtures

| File                          | Purpose                                     |
| ----------------------------- | ------------------------------------------- |
| `tests/fixtures/app.py`       | Test app factory, client, principal binding |
| `tests/fixtures/handlers.py`  | Complete mock handler registry              |
| `tests/fixtures/factories.py` | Deterministic DTO factories                 |
| `tests/fixtures/problem.py`   | Problem detail assertions                   |
| `tests/fixtures/auth.py`      | JWT and actor helpers                       |
| `tests/fixtures/seed.py`      | E2E database seed                           |
| `tests/fixtures/outbox.py`    | Outbox inspection and drain                 |

## Related existing suites

These pre-existing suites complement but are outside this deliverable scope:

- `tests/unit/` — domain and delivery unit tests
- `tests/integration/` — repository adapter integration
- `tests/workflows/` — legacy E2E workflow tests
- `tests/smoke/` — legacy smoke tests
- `tests/performance/`, `tests/load/`, `tests/stress/` — non-functional validation

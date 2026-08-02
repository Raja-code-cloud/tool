# Regression Test Plan

## Purpose

This plan defines the automated regression strategy for the Cloud Content Hub backend after implementation completion. Tests validate API contracts, module behavior, critical business workflows, and negative/error paths without modifying application business logic.

## Scope

| Area               | Suite location                                          | Markers             |
| ------------------ | ------------------------------------------------------- | ------------------- |
| Authentication     | `tests/regression/`, `tests/api/test_auth.py`           | `regression`, `api` |
| Asset management   | `tests/api/test_assets_api.py`, `tests/regression/`     | `regression`, `api` |
| Content generation | `tests/api/test_content_api.py`, `tests/automation/`    | `api`, `automation` |
| Publishing         | `tests/api/test_publishing_api.py`, `tests/automation/` | `api`, `automation` |
| Scheduling         | `tests/api/test_scheduler_api.py`, `tests/automation/`  | `api`, `automation` |
| Analytics          | `tests/api/test_analytics_api.py`, `tests/automation/`  | `api`, `automation` |
| Notifications      | `tests/api/test_notifications_admin_api.py`             | `api`, `automation` |
| Administration     | `tests/api/test_notifications_admin_api.py`             | `api`, `regression` |

## Regression packs

### Smoke (`tests/regression/test_smoke.py`)

- **Goal:** Fast signal on every pull request.
- **Duration target:** under 30 seconds.
- **Marker:** `smoke` + `regression`.
- **Infrastructure:** mocked handlers, no database.

### Critical path (`tests/regression/test_critical_path.py`)

- **Goal:** Validate upload → generate → publish → schedule flows.
- **Marker:** `critical_path` + `regression`.
- **Infrastructure:** mocked handlers.

### Full regression (`tests/regression/test_full_regression.py`)

- **Goal:** Read-route coverage across all API modules.
- **Marker:** `regression`.
- **Infrastructure:** mocked handlers.

### Nightly (`tests/regression/test_nightly.py`)

- **Goal:** Extended admin/analytics coverage.
- **Marker:** `nightly` + `slow` + `regression`.
- **Infrastructure:** mocked handlers; pairs with integration automation.

## Supporting suites

| Suite               | Path                | Role                                              |
| ------------------- | ------------------- | ------------------------------------------------- |
| API automation      | `tests/api/`        | Request/response models, pagination, auth, errors |
| Workflow automation | `tests/automation/` | Real DB + handler orchestration                   |
| Contract            | `tests/contract/`   | Envelope and error-code stability                 |
| Fixtures            | `tests/fixtures/`   | Deterministic factories and mock handlers         |

## Out of scope

- Business logic changes
- Repository/provider implementation changes
- Frontend testing
- Performance tuning (covered by `tests/performance/` separately)

## Entry criteria

- Backend implementation complete
- Python 3.13, Ruff clean, mypy strict
- Deterministic fixtures with no wall-clock or network dependency in smoke/API/regression packs

## Exit criteria

- All regression packs pass in CI
- API automation covers documented endpoints
- Workflow automation covers upload, generate, publish, schedule, analytics, notifications
- Negative tests cover auth, permissions, invalid payloads
- Documentation complete in this directory

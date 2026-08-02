# Backend Operations

Operational configuration for Cloud Content Hub AI production readiness. This directory
contains probe definitions, capacity guidance, and validation scripts. It does not
contain application business logic.

## Contents

| Path | Purpose |
| ---- | ------- |
| `probes.yaml` | Liveness, readiness, and startup probe definitions for all runtime units |
| `capacity.yaml` | Connection pool, scaling, and sizing recommendations |
| `compose/monitoring-stack.yml` | Local Prometheus + Grafana stack for SRE validation |
| `scripts/validate_health.sh` | Verify health endpoints against a running API |
| `scripts/validate_alerts.py` | Validate Prometheus alert rule syntax |

## Health probe routes

The FastAPI application exposes canonical unversioned probes:

| Probe | Path | Expected |
| ----- | ---- | -------- |
| Informational | `/health` | 200 |
| Liveness | `/live` | 200 |
| Readiness | `/ready` | 200 (PostgreSQL + Redis) |

Deployment infrastructure (Docker, ACA Bicep) may reference `/health/live` and
`/health/ready`. Align infra probe paths with the implemented routes above, or add
route aliases in a future operational patch. See `docs/backend/sre/OPERATIONS_GUIDE.md`.

## Quick validation

```bash
# Local API (default http://127.0.0.1:8000)
./backend/operations/scripts/validate_health.sh

# Remote environment
./backend/operations/scripts/validate_health.sh https://ca-cch-api-dev.example.com

# Alert rule syntax
python backend/operations/scripts/validate_alerts.py
```

## Related documentation

- `docs/backend/sre/MONITORING.md`
- `docs/backend/sre/ALERTS.md`
- `docs/backend/sre/RUNBOOKS.md`
- `docs/backend/sre/OPERATIONS_GUIDE.md`

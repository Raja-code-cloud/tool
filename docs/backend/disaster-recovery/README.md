# Disaster Recovery

Operational disaster recovery and business continuity documentation for the Cloud Content Hub AI backend.

## Scope

This directory covers backup, restore, failover, and recovery validation for platform dependencies:

| Dependency | Platform service | Recovery owner |
| ---------- | ---------------- | -------------- |
| Relational data | Azure Database for PostgreSQL 17 | Platform / DBA |
| Object storage | Azure Blob Storage (GRS) | Platform / Storage |
| Cache and queues | Azure Cache for Redis | Platform / SRE |
| Secrets | Azure Key Vault | Security / Platform |
| Compute | Azure Container Apps | Platform / SRE |
| Observability | Log Analytics | Platform / SRE |

Application code is immutable across environments. Recovery reuses promoted container images and restores data plane dependencies.

## Documents

| Document | Purpose |
| -------- | ------- |
| [BACKUP_STRATEGY.md](BACKUP_STRATEGY.md) | Automated backup scope, retention, and verification |
| [RESTORE_GUIDE.md](RESTORE_GUIDE.md) | Step-by-step restore procedures per dependency |
| [FAILOVER_PLAN.md](FAILOVER_PLAN.md) | Failover paths for component and regional outages |
| [RTO_RPO.md](RTO_RPO.md) | Recovery time and point objectives |
| [DISASTER_RECOVERY_RUNBOOK.md](DISASTER_RECOVERY_RUNBOOK.md) | Scenario playbooks and checklists |
| [BUSINESS_CONTINUITY_PLAN.md](BUSINESS_CONTINUITY_PLAN.md) | Operational dependencies and continuity policy |

## Automated validation

Recovery behavior is validated by pytest suites (no live Azure calls required):

```bash
cd backend
pytest tests/disaster_recovery tests/backup tests/failover -m "not integration"
```

Integration-marked tests require a configured PostgreSQL instance.

## Related documents

- `docs/backend/devops/RUNBOOK.md`
- `docs/backend/devops/ROLLBACK.md`
- `docs/backend/devops/AZURE_CONTAINER_APPS.md`
- `docs/backend/events/OUTBOX_PATTERN.md`
- `docs/backend/SECURITY_GUIDELINES.md`
- `docs/backend/release/RC_CHECKLIST.md`

## Drill cadence

| Drill | Frequency | Environment |
| ----- | --------- | ----------- |
| PostgreSQL PITR restore to isolated server | Quarterly | QA or DR |
| Key Vault secret rotation with redeploy | Semi-annual | Dev → QA |
| ACA revision rollback | After each prod deploy | Prod (canary) |
| Regional DR tabletop | Annual | DR (westus2) |
| Outbox lag / worker recovery simulation | Monthly | CI (automated) |

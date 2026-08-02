# RTO and RPO

Recovery Time Objective (RTO) and Recovery Point Objective (RPO) targets for Cloud Content Hub AI backend services.

## Definitions

| Term | Meaning |
| ---- | ------- |
| **RPO** | Maximum acceptable data loss measured in time before the incident |
| **RTO** | Maximum acceptable downtime before service is restored to defined capacity |
| **MTPD** | Maximum Tolerable Period of Disruption — business deadline before severe impact |

## Service tier classification

Cloud Content Hub backend is **Tier 1** (business-critical):

- Content generation and publishing depend on API availability.
- Scheduled publishing requires beat and worker uptime.
- Tenant data loss is unacceptable.

## Objectives by component

| Component | RPO | RTO | Notes |
| --------- | --- | --- | ----- |
| PostgreSQL (prod) | ≤ 5 minutes | ≤ 4 hours | Azure PITR; HA failover ≤ 60 seconds for server failure |
| PostgreSQL (dev/qa) | ≤ 24 hours | ≤ 8 hours | Lower retention acceptable |
| Blob storage (GRS) | ≤ 15 minutes | ≤ 4 hours | GRS replication lag; account failover adds time |
| Redis (default) | Best effort (queue) | ≤ 30 minutes | Outbox compensates for lost Celery messages |
| Redis (with persistence) | ≤ 1 hour | ≤ 1 hour | Optional premium tier |
| Key Vault secrets | 0 (versioned) | ≤ 15 minutes | Redeploy ACA after secret update |
| API containers | 0 | ≤ 15 minutes | Revision rollback or redeploy |
| Worker containers | 0 | ≤ 30 minutes | Scale + redeploy; outbox catches up |
| Beat scheduler | ≤ 5 minutes | ≤ 15 minutes | Missed schedules may require manual catch-up |
| Outbox events | 0 (transactional) | ≤ 1 hour | Persisted in PostgreSQL; redispatch after recovery |
| Container images (ACR) | 0 | ≤ 10 minutes | Immutable tags in geo-redundant registry |
| Log Analytics | ≤ 1 hour | N/A (non-blocking) | Operational visibility only |
| AI providers | N/A | ≤ 4 hours | External dependency; degrade gracefully |
| Identity providers | N/A | ≤ 4 hours | External OIDC; cached JWKS mitigates brief outages |

## Scenario matrix

| Scenario | RPO achieved | RTO target | Primary procedure |
| -------- | ------------ | ---------- | ----------------- |
| Bad deploy | 0 | 15 min | `ROLLBACK.md` |
| API container crash | 0 | 2 min | ACA auto-restart |
| Worker crash | 0 (outbox) | 5 min | ACA auto-restart + scale |
| Database connection exhaustion | 0 | 30 min | Pool tuning, scale down API |
| PostgreSQL server failure (HA) | ≤ 5 min | 60 sec | Azure automatic failover |
| PostgreSQL corruption | PITR timestamp | 4 hours | `RESTORE_GUIDE.md` §1 |
| Redis total loss | Queue best effort | 30 min | Recreate + redeploy |
| Blob accidental delete | 0 (soft delete) | 1 hour | Undelete |
| Blob regional loss | ≤ 15 min | 4 hours | GRS account failover |
| Key Vault secret compromise | 0 | 1 hour | Rotate + redeploy |
| Outbox dispatcher stopped | 0 | 1 hour | Restart workers |
| Regional outage (eastus) | ≤ 15 min | 8 hours | `FAILOVER_PLAN.md` §Regional DR |
| Provider outage (AI/OIDC) | N/A | 4 hours | Fail closed / secondary provider |

## Business impact thresholds

| Duration | Impact |
| -------- | ------ |
| < 5 min | Minimal — retries and client backoff absorb |
| 5–30 min | Degraded — scheduled publishing may delay |
| 30 min – 4 hours | Significant — content workflows blocked |
| > 4 hours | Severe — activate BCP customer communication |

## Measurement

Track actual recovery performance during drills:

| Metric | Source | Drill frequency |
| ------ | ------ | --------------- |
| PITR restore duration | Manual drill log | Quarterly |
| Rollback time-to-ready | Deploy pipeline | Each prod deploy |
| Outbox catch-up time | Prometheus / Log Analytics | Monthly simulation |
| DR activation end-to-end | Tabletop + DR deploy | Annual |

Record in incident tickets:

- Incident start (detection time)
- Recovery start (mitigation action time)
- Service restored (readiness 200 sustained)
- RPO achieved (latest committed transaction timestamp)
- RTO achieved (restored − start)

## Dependencies outside RTO/RPO scope

These dependencies are documented but not guaranteed by backend DR:

- Frontend application and CDN
- Customer DNS and custom domains (except DR cutover procedure)
- Third-party social platform APIs
- Email/SMS notification delivery providers

## Review cadence

Review RTO/RPO targets:

- After every SEV-1 incident
- After quarterly restore drill
- Annually with business stakeholders

Update this document when Azure tier, retention policy, or architecture changes.

# Business Continuity Plan

Business continuity policy and operational dependencies for Cloud Content Hub AI backend.

## Purpose

Ensure the backend can maintain or rapidly restore essential content management, generation, and publishing capabilities after disruptive events.

## Critical business functions

| Function               | Backend dependency                 | Maximum tolerable disruption  |
| ---------------------- | ---------------------------------- | ----------------------------- |
| User authentication    | API + OIDC + PostgreSQL            | 4 hours                       |
| Content CRUD           | API + PostgreSQL + Blob            | 4 hours                       |
| AI content generation  | API + AI provider + PostgreSQL     | 8 hours (degraded acceptable) |
| Scheduled publishing   | Beat + Worker + PostgreSQL + Redis | 4 hours                       |
| Asset upload/download  | API + Blob + PostgreSQL            | 4 hours                       |
| Notifications          | Worker + outbox + PostgreSQL       | 8 hours                       |
| Administration / audit | API + PostgreSQL                   | 4 hours                       |

## Operational dependencies

### Internal (platform)

```text
                    ┌─────────────────┐
                    │  Azure Front Door│
                    │  / Traffic Mgr   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Container Apps │
                    │  API / Worker   │
                    │  / Beat         │
                    └────────┬────────┘
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
    │ PostgreSQL  │   │    Redis    │   │ Blob Storage│
    │   17        │   │   (Celery)  │   │    (GRS)    │
    └─────────────┘   └─────────────┘   └─────────────┘
           │
    ┌──────▼──────┐
    │  Key Vault  │
    │  (secrets)  │
    └─────────────┘
```

| Dependency    | Required for             | Fallback                     |
| ------------- | ------------------------ | ---------------------------- |
| PostgreSQL    | All persistent state     | PITR restore, DR geo-restore |
| Redis         | Celery broker, cache     | Recreate; outbox replay      |
| Blob storage  | Media assets             | GRS failover, soft delete    |
| Key Vault     | Connection strings, keys | Secret recovery, rotation    |
| ACR           | Container images         | Geo-redundant registry       |
| Log Analytics | Incident diagnosis       | Non-blocking; alternate logs |

### External

| Provider                       | Function            | Fallback                               |
| ------------------------------ | ------------------- | -------------------------------------- |
| OIDC identity (Azure AD, etc.) | Authentication      | Cached JWKS; fail closed               |
| OpenAI / Anthropic / Gemini    | AI generation       | Secondary provider or maintenance mode |
| Social platforms               | Publishing delivery | Retry queue; manual republish          |
| Azure platform                 | All infrastructure  | DR region activation                   |

## Recovery priorities

Restore in order:

1. **PostgreSQL** — source of truth for tenants, content metadata, outbox.
2. **Key Vault secrets** — enable secure connection to restored services.
3. **Redis** — unblock async processing.
4. **API containers** — restore read/write HTTP surface.
5. **Worker + beat** — resume publishing and integrations.
6. **Blob storage** — restore media access (may parallelize with step 4).
7. **Observability** — restore visibility (non-blocking for service restoration).

## Manual recovery procedures

Procedures requiring human decision:

| Procedure                  | Document                                | Trigger                 |
| -------------------------- | --------------------------------------- | ----------------------- |
| PostgreSQL PITR            | RESTORE_GUIDE.md §1                     | Data corruption         |
| Regional DR activation     | FAILOVER_PLAN.md §Regional DR           | Regional outage         |
| Blob account failover      | RESTORE_GUIDE.md §2                     | Storage region loss     |
| Secret compromise rotation | RESTORE_GUIDE.md §4                     | Security incident       |
| Dead letter replay         | DISASTER_RECOVERY_RUNBOOK.md §Outbox    | Exhausted event retries |
| Missed schedule catch-up   | DISASTER_RECOVERY_RUNBOOK.md §Scheduler | Extended beat outage    |

Automated recovery (no manual intervention):

- ACA container restart on liveness failure
- PostgreSQL HA automatic failover
- Outbox redispatch after worker recovery
- Celery task retries for transient failures

## Communication plan

| Audience    | Channel            | Owner              | Timing              |
| ----------- | ------------------ | ------------------ | ------------------- |
| Engineering | Slack #incidents   | Incident commander | Immediate           |
| Leadership  | Email / phone tree | Incident commander | SEV-1 within 30 min |
| Customers   | Status page        | Support lead       | SEV-1 within 60 min |
| Compliance  | Secure channel     | Security officer   | Data loss events    |

Status page message template:

> We are investigating elevated errors affecting content publishing. API authentication and read operations may be impacted. Updates every 30 minutes.

## Emergency contacts (placeholders)

Replace with your organization's contact details:

| Role                     | Name                | Contact                     | Escalation            |
| ------------------------ | ------------------- | --------------------------- | --------------------- |
| Incident commander       | On-call SRE         | oncall-platform@example.com | Primary               |
| Backend lead             | Engineering manager | backend-lead@example.com    | SEV-1                 |
| Database administrator   | DBA team            | dba-team@example.com        | Data loss             |
| Security officer         | InfoSec             | security@example.com        | Credential compromise |
| Azure subscription owner | Cloud platform      | azure-admin@example.com     | Regional DR           |
| Customer support lead    | Support             | support-lead@example.com    | Customer comms        |
| Executive sponsor        | VP Engineering      | vp-eng@example.com          | SEV-0                 |

## Work-from-home / alternate site

Backend recovery is cloud-native. Engineers require:

- VPN or zero-trust access to Azure subscription
- `az` CLI authenticated
- GitHub access for deployment workflows
- Secure access to Key Vault (RBAC)

No physical datacenter access required.

## Testing and maintenance

| Activity                  | Frequency          | Owner               |
| ------------------------- | ------------------ | ------------------- |
| Automated DR tests (CI)   | Every PR / nightly | Engineering         |
| PostgreSQL restore drill  | Quarterly          | DBA                 |
| DR tabletop exercise      | Annual             | SRE + Leadership    |
| BCP document review       | Annual             | Engineering manager |
| Contact list verification | Semi-annual        | Incident commander  |

Run automated validation:

```bash
cd backend
pytest tests/disaster_recovery tests/backup tests/failover
```

## Document control

| Version | Date       | Author      | Changes     |
| ------- | ---------- | ----------- | ----------- |
| 1.0     | 2026-08-02 | DR Engineer | Initial BCP |

Next review date: 2027-02-02

## Related documents

- [RTO_RPO.md](RTO_RPO.md)
- [BACKUP_STRATEGY.md](BACKUP_STRATEGY.md)
- [DISASTER_RECOVERY_RUNBOOK.md](DISASTER_RECOVERY_RUNBOOK.md)
- `docs/backend/SECURITY_GUIDELINES.md`
- `docs/backend/devops/ENVIRONMENTS.md`

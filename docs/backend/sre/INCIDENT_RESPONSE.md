# Incident Response

Incident lifecycle for Cloud Content Hub AI backend production issues.

## Severity classification

| Level | Criteria                          | Response                    | Examples                                 |
| ----- | --------------------------------- | --------------------------- | ---------------------------------------- |
| SEV-1 | Complete outage or data loss risk | Page immediately, war room  | API down, DB unavailable                 |
| SEV-2 | Major degradation, SLO burn       | Page on-call, async updates | High 5xx, worker fleet down              |
| SEV-3 | Partial degradation               | Slack notification          | Single provider outage, elevated latency |
| SEV-4 | Minor issue, no user impact       | Ticket, next business day   | Warning alerts, non-prod                 |

Map alert severity to incident level:

- `critical` alerts → SEV-1 or SEV-2
- `warning` alerts → SEV-3 or SEV-4

## Incident lifecycle

```text
Detect → Triage → Mitigate → Resolve → Post-mortem
```

### 1. Detect

Sources:

- Prometheus alerts via Alertmanager
- ACA health probe failures
- User reports / support tickets
- CI/CD smoke test failures

### 2. Triage (first 15 minutes)

1. Acknowledge alert in paging system.
2. Identify affected component (API, worker, DB, Redis, storage, provider).
3. Check Grafana dashboards:
   - API: `cch-api`
   - Workers: `cch-workers`
   - Infrastructure: `cch-infrastructure`
4. Determine severity level.
5. Open incident channel/document with timeline.

### 3. Mitigate

Follow runbook for affected component (`RUNBOOKS.md`):

| Component  | Runbook                 |
| ---------- | ----------------------- |
| API        | `#api-unavailable`      |
| Database   | `#database-unavailable` |
| Redis      | `#redis-unavailable`    |
| Storage    | `#blob-storage-failure` |
| Workers    | `#worker-crash`         |
| Scheduler  | `#scheduler-failure`    |
| Outbox     | `#outbox-backlog`       |
| Providers  | `#provider-outage`      |
| Bad deploy | `#deployment-rollback`  |

Prefer mitigation over root-cause during active incident:

- Roll back revision if deploy-correlated
- Scale replicas if capacity-bound
- Fail over dependency if platform supports it

### 4. Resolve

Confirm:

1. Alerts auto-resolved in Alertmanager.
2. SLI metrics returned to target (check analytics dashboard).
3. Health probes pass: `./backend/operations/scripts/validate_health.sh`
4. No new errors in Log Analytics for 15 minutes.

Communicate resolution to stakeholders.

### 5. Post-mortem (within 5 business days)

Required for SEV-1 and SEV-2. Template:

| Section              | Content                                |
| -------------------- | -------------------------------------- |
| Summary              | What happened, duration, impact        |
| Timeline             | Detect → mitigate → resolve timestamps |
| Root cause           | Technical cause (5 whys)               |
| Contributing factors | Deploy, capacity, missing alert, etc.  |
| Action items         | Prevent recurrence, improve detection  |
| SLO impact           | Error budget consumed                  |

Blameless culture — focus on systems and processes.

## Communication

| Audience    | SEV-1/2                       | SEV-3            | SEV-4  |
| ----------- | ----------------------------- | ---------------- | ------ |
| Engineering | Real-time in incident channel | Slack update     | Ticket |
| Product     | Status every 30 min           | End notification | None   |
| Users       | Status page if user-facing    | If affected      | None   |

## Escalation

1. **Primary on-call** — platform team (15 min SLA for critical).
2. **Secondary on-call** — if primary unresponsive after 15 min.
3. **Engineering lead** — SEV-1 lasting > 1 hour.
4. **Security on-call** — auth alerts (`CchAuthFailureSpike`), suspected breach.

Define rotation in team wiki; this document covers procedures only.

## Security incidents

For suspected breach or credential compromise:

1. Engage security on-call immediately.
2. Rotate affected Key Vault secrets.
3. Redeploy all containers to pick up new secrets.
4. Preserve logs for forensics (do not delete Log Analytics data).
5. See `docs/backend/SECURITY_GUIDELINES.md`.

## Related

- `RUNBOOKS.md` — component runbooks
- `ALERTS.md` — alert catalog
- `SLOS.md` — error budget tracking
- `docs/backend/devops/RUNBOOK.md` — infrastructure procedures

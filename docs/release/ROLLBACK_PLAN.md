# Rollback Plan — Cloud Content Hub AI Frontend RC1

This document defines rollback procedures for frontend deployments from GitHub Release artifacts.

**Scope:** Frontend Next.js server deployment  
**Target version:** v1.0.0-rc.1  
**Related:** [RELEASE_PROCESS.md](../frontend/RELEASE_PROCESS.md) · [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) · [GO_LIVE_CHECKLIST.md](./GO_LIVE_CHECKLIST.md)

---

## Rollback triggers

Initiate rollback when any of the following occur post-deploy:

| Trigger                            | Examples                                                                         |
| ---------------------------------- | -------------------------------------------------------------------------------- |
| **Availability**                   | Service unreachable, crash loop, sustained 5xx error rate                        |
| **Critical functional regression** | Dashboard or shell fails to render; navigation broken                            |
| **Security incident**              | Accidental secret exposure, compromised artifact, critical CVE in deployed build |
| **Performance collapse**           | Response times exceed agreed threshold with no quick mitigation                  |
| **Failed smoke tests**             | Post-deploy checklist failures that cannot be hot-patched within SLA             |

**Do not rollback for:**

- Known mock-data limitations documented in [KNOWN_ISSUES.md](./KNOWN_ISSUES.md)
- Calendar placeholder behavior (pre-existing)
- Decorative global search or non-functional analytics date filter (pre-existing)
- Issues requiring code fix — prefer forward fix via new patch release after revert on `main`

---

## Rollback principles

1. **Roll forward with a previous artifact** — redeploy last known-good tarball; do not delete or retag releases
2. **Immutable tags** — never force-push or move `v*` tags
3. **Time-bound decision** — default rollback decision window: 30 minutes from incident detection
4. **Communicate early** — notify stakeholders when rollback starts, not when it completes
5. **Preserve evidence** — retain logs and failing artifact for post-incident review

---

## Rollback decision matrix

| Severity | User impact                             | Action                       | Target time |
| -------- | --------------------------------------- | ---------------------------- | ----------- |
| SEV-1    | Total outage or data/security risk      | Immediate rollback           | < 15 min    |
| SEV-2    | Major feature broken (shell, dashboard) | Rollback unless fix < 30 min | < 30 min    |
| SEV-3    | Minor route issue, workaround exists    | Forward fix preferred        | Next patch  |
| SEV-4    | Cosmetic / known limitation             | No rollback                  | N/A         |

---

## RC1 baseline

For the first RC1 deployment, there is no prior production release. Rollback options:

| Scenario                     | Action                                                              |
| ---------------------------- | ------------------------------------------------------------------- |
| RC1 deploy fails smoke tests | Do not promote; fix forward or redeploy previous staging artifact   |
| RC1 promoted then fails      | Redeploy last known-good staging build (pre-RC1 artifact or commit) |
| No prior artifact exists     | Take application offline; redeploy from validated `main` commit     |

After first successful RC1 deploy, update the release pointer:

```
CURRENT_STAGING=v1.0.0-rc.1
PREVIOUS_STAGING=<none or prior build>
CURRENT_PRODUCTION=<unset until GA>
PREVIOUS_PRODUCTION=<unset>
```

---

## Rollback procedure

### Step 1 — Halt and assess (0–5 min)

- [ ] Stop in-progress deployment if still running
- [ ] Confirm incident severity with on-call
- [ ] Incident commander declares rollback
- [ ] Start incident channel / ticket

### Step 2 — Prepare previous artifact (5–10 min)

```sh
# Download from GitHub Releases
# cloud-content-hub-frontend-v<PREV_VERSION>.tar.gz

mkdir -p /opt/cloud-content-hub-frontend-rollback
cd /opt/cloud-content-hub-frontend-rollback
tar -xzf cloud-content-hub-frontend-v<PREV_VERSION>.tar.gz
npm ci --omit=dev --no-audit --no-fund
```

- [ ] Artifact version matches documented previous release
- [ ] Extract completed without errors
- [ ] Environment variables match production runbook

### Step 3 — Redeploy (10–20 min)

**Option A — Directory swap (single host)**

```sh
systemctl stop cloud-content-hub-frontend
mv /opt/cloud-content-hub-frontend /opt/cloud-content-hub-frontend-failed
mv /opt/cloud-content-hub-frontend-rollback /opt/cloud-content-hub-frontend
systemctl start cloud-content-hub-frontend
```

**Option B — Container / platform rollback**

- Redeploy previous container image or platform revision pinned to prior release artifact
- Update traffic routing to previous revision

- [ ] Process started successfully
- [ ] No crash loop in logs

### Step 4 — Verify recovery (20–30 min)

| Test                            | Pass |
| ------------------------------- | ---- |
| `/` redirects to `/dashboard`   | [ ]  |
| `/dashboard` returns 200        | [ ]  |
| Shell navigation works          | [ ]  |
| Error rate returned to baseline | [ ]  |
| Monitoring green                | [ ]  |

- [ ] Incident commander confirms service restored
- [ ] Update release pointer to rolled-back version

### Step 5 — Communicate (parallel with Steps 3–4)

- [ ] Internal: incident channel updated with status
- [ ] External (if applicable): status page / customer notice
- [ ] Document rollback version and start/end times

### Step 6 — Post-rollback (within 24 h)

- [ ] Preserve failed deployment directory/logs for analysis
- [ ] Create incident report with timeline
- [ ] Open revert PR on `main` if bad commit merged
- [ ] Plan forward patch or RC2 release after fix validated
- [ ] Update [CHANGELOG.md](./CHANGELOG.md) if customer-visible rollback occurred

---

## Recovery checklist

```
Rollback version:     v__________
Rollback started:     __________ UTC
Rollback completed:   __________ UTC
Executed by:          __________
Verified by:          __________
Smoke tests pass:     [ ] Yes  [ ] No
Monitoring normal:    [ ] Yes  [ ] No
Stakeholders notified:[ ] Yes  [ ] No
Incident ticket:      __________
Root cause summary:   __________
Forward fix ticket:   __________
```

---

## Failed rollback contingencies

| Situation                    | Action                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------- |
| Previous artifact also fails | Escalate SEV-1; deploy known stable commit build; engage platform team              |
| Artifact unavailable         | Retrieve from 90-day GitHub Actions artifact retention or backup storage            |
| Database migration (future)  | N/A for RC1 mock frontend; document forward-only migrations when backend integrates |
| Partial deploy (CDN cached)  | Purge CDN cache; confirm cache TTL headers                                          |

---

## Code fix path (after rollback)

1. Revert offending commit(s) on `main` via pull request
2. Wait for CI green (`ci.yml` / `build.yml`)
3. Cut patch or RC release (e.g., `1.0.0-rc.2`) via **Release Frontend** workflow
4. Deploy new version through standard [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
5. Do **not** redeploy the failed version tag

---

## Prevention measures

- Always deploy validated GitHub Release artifacts, never ad-hoc builds
- Keep release pointer updated after each successful deploy
- Run full smoke tests before marking deploy complete
- Require GitHub Environment approval for production
- Resolve CI blockers before cutting release tags
- Maintain staging deploy parity with production process
- Restrict RC1 to network-controlled environments

---

## Contact escalation

Define before production launch:

| Level                  | Contact | Method |
| ---------------------- | ------- | ------ |
| L1 On-call             | _TBD_   | _TBD_  |
| L2 Frontend lead       | _TBD_   | _TBD_  |
| L3 Platform / DevOps   | _TBD_   | _TBD_  |
| L4 Product / Executive | _TBD_   | _TBD_  |

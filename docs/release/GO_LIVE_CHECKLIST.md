# Go-Live Checklist — Cloud Content Hub AI Frontend RC1

Use this checklist for RC1 staging go-live and as the template for future GA promotion.

**Target version:** `v1.0.0-rc.1`  
**Assessment date:** 2026-08-02  
**Related:** [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) · [RELEASE_SIGNOFF.md](./RELEASE_SIGNOFF.md) · [ROLLBACK_PLAN.md](./ROLLBACK_PLAN.md)

---

## Pre-go-live (T-7 to T-1 days)

### Repository and release readiness

- [ ] `main` branch contains intended RC1 commit
- [ ] TypeScript, ESLint, Vitest, and build pass on target commit
- [ ] CI blockers resolved (`format:check` script + Prettier drift)
- [ ] [CHANGELOG.md](./CHANGELOG.md) updated with `1.0.0-rc.1` section
- [ ] [RELEASE_NOTES_RC1.md](./RELEASE_NOTES_RC1.md) reviewed and approved
- [ ] [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) reviewed by Product and Support
- [ ] [RELEASE_SIGNOFF.md](./RELEASE_SIGNOFF.md) signed for staging scope
- [ ] Semantic version `1.0.0-rc.1` does not already exist as tag or release

### Security and compliance

- [ ] Dependency review passed on final commit
- [ ] `npm audit --omit=dev` returns 0 high/critical vulnerabilities
- [ ] No secrets in repository, artifacts, or `NEXT_PUBLIC_*` variables
- [ ] Security headers verified in `lib/security/headers.ts`
- [ ] [FRONTEND_SECURITY_CHECKLIST.md](../frontend/FRONTEND_SECURITY_CHECKLIST.md) reviewed
- [ ] Artifact access policy defined (public vs private repository)
- [ ] Network-level access control planned (VPN, IP allowlist, or IAP)

### Infrastructure

- [ ] Staging environment provisioned (Node.js 22.22.1)
- [ ] TLS certificate installed and valid
- [ ] DNS configured for staging URL
- [ ] Reverse proxy / load balancer configured
- [ ] Environment variables set (`NODE_ENV`, `NEXT_PUBLIC_APP_ENV`)
- [ ] Log aggregation connected
- [ ] Uptime monitor configured for `/dashboard`
- [ ] Rollback artifact path documented

### Operational readiness

- [ ] [ROLLBACK_PLAN.md](./ROLLBACK_PLAN.md) walkthrough completed with ops
- [ ] On-call rotation confirmed (contacts TBD — see rollback plan)
- [ ] Incident response runbook linked
- [ ] Change ticket / deployment request approved
- [ ] Stakeholder communication drafted

---

## Go-live day (T-0)

### Release cut

- [ ] Trigger **Actions → Release Frontend → Run workflow**
- [ ] Version: `1.0.0-rc.1`
- [ ] Prerelease: **enabled**
- [ ] Workflow validation passes (typecheck, format, lint, test, build)
- [ ] GitHub Release created with artifact attached
- [ ] Tag `v1.0.0-rc.1` points to validated commit

### Deploy to staging

- [ ] Download `cloud-content-hub-frontend-v1.0.0-rc.1.tar.gz`
- [ ] Extract to staging host
- [ ] Run `npm ci --omit=dev`
- [ ] Start application with process supervisor
- [ ] Confirm application starts without crash loop

### Smoke tests (within 15 minutes)

| #   | Test                         | Expected result                    | Pass |
| --- | ---------------------------- | ---------------------------------- | ---- |
| 1   | Root redirect `/` → `/dashboard` | 307/308                       | [ ]  |
| 2   | Dashboard loads              | 200; shell with sidebar            | [ ]  |
| 3   | All nav routes                 | No client errors                   | [ ]  |
| 4   | Theme toggle                   | Persists on reload                 | [ ]  |
| 5   | Upload wizard                  | Steps advance; draft in localStorage | [ ] |
| 6   | Calendar placeholder           | Coming-soon UI displays            | [ ]  |
| 7   | Responsive (375px, 1440px)     | Shell usable                       | [ ]  |
| 8   | Browser console                | No uncaught errors on primary flows | [ ] |
| 9   | Security headers               | CSP, X-Frame-Options, nosniff      | [ ]  |

- [ ] Smoke test results recorded (tester, timestamp, environment)
- [ ] Monitoring dashboards show healthy metrics

### Communication

- [ ] Internal announcement sent with release notes link
- [ ] Support briefed on mock-data limitations
- [ ] On-call notified of version and rollback pointer

---

## Post-go-live (T+1 to T+7 days)

### Monitoring watch

- [ ] 24-hour error rate review completed
- [ ] No SEV-1 or SEV-2 incidents attributable to RC1
- [ ] Performance within acceptable range for staging
- [ ] No unexpected security header or CSP violations

### Validation

- [ ] Product walkthrough of primary workflows completed
- [ ] UX audit findings acknowledged (decorative search, calendar nav)
- [ ] RC3 Principal Review results incorporated
- [ ] Feedback collected from staging users

### Release pointer update

```
CURRENT_STAGING=v1.0.0-rc.1
DEPLOY_TIMESTAMP=__________
DEPLOYED_BY=__________
SMOKE_TEST_PASS=[ ] Yes  [ ] No
```

---

## GA promotion gate (RC1 → 1.0.0)

Do **not** promote to production GA until all items pass:

- [ ] RC1 staging validation complete (minimum 7 days recommended)
- [ ] RC3 Principal Review passed
- [ ] All blockers in [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) resolved or explicitly waived
- [ ] CI fully green including format check
- [ ] Production environment with GitHub approval configured
- [ ] On-call escalation contacts populated
- [ ] Customer-facing support documentation updated
- [ ] Authentication strategy defined (even if not yet implemented)
- [ ] [RELEASE_SIGNOFF.md](./RELEASE_SIGNOFF.md) updated for GA scope

---

## Go / No-Go decision record

| Field                | Value                          |
| -------------------- | ------------------------------ |
| Decision             | **GO WITH MINOR RISKS** (staging) |
| Decision date        | 2026-08-02                     |
| Approved by          | Release Manager (pending co-signatures) |
| Scope                | Staging / internal validation only |
| Blockers for workflow| `format:check` script + Prettier drift |
| Blockers for GA      | RC3 Principal Review pending   |

---

## Rollback quick reference

If smoke tests fail or SEV-1/SEV-2 incident occurs:

1. Stop deployment promotion
2. Follow [ROLLBACK_PLAN.md](./ROLLBACK_PLAN.md)
3. Notify incident channel
4. Document in change ticket
5. Plan forward fix via PR → new RC or patch release

**Do not** delete or retag `v1.0.0-rc.1` once published.

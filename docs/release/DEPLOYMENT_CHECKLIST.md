# Deployment Checklist — Cloud Content Hub AI Frontend

Use this checklist when deploying a versioned frontend release to staging or production.

**Related docs:** [DEPLOYMENT_GUIDE.md](../frontend/DEPLOYMENT_GUIDE.md) · [RELEASE_PROCESS.md](../frontend/RELEASE_PROCESS.md) · [ROLLBACK_PLAN.md](./ROLLBACK_PLAN.md)

---

## Phase 1 — Pre-deploy validation

### Release artifact

- [ ] GitHub Release exists for target version (e.g., `v1.0.0`)
- [ ] Artifact downloaded: `cloud-content-hub-frontend-v<version>.tar.gz`
- [ ] Artifact SHA verified against GitHub Release assets (if checksum published)
- [ ] Release commit matches expected `main` HEAD or documented hotfix commit

### Quality gates (must be green on release commit)

- [ ] `npm run typecheck` — pass
- [ ] `npm run format:check` — pass
- [ ] `npm run lint` — pass
- [ ] `npm run test:run` — pass
- [ ] `npm run build` — pass

### Approvals

- [ ] Release notes reviewed ([RELEASE_NOTES.md](./RELEASE_NOTES.md))
- [ ] Known limitations acknowledged ([KNOWN_LIMITATIONS.md](./KNOWN_LIMITATIONS.md))
- [ ] Product sign-off for mock-data behavior
- [ ] Security sign-off for artifact exposure policy
- [ ] GitHub `production` environment approval obtained (if configured)

---

## Phase 2 — Environment preparation

### Runtime requirements

| Requirement     | Value                                                        |
| --------------- | ------------------------------------------------------------ |
| Node.js         | >= 22.22.1                                                   |
| Package manager | npm (use lockfile)                                           |
| Process manager | Platform-specific (systemd, PM2, container entrypoint, etc.) |
| Port            | Platform default or `PORT` env var                           |

### Environment variables

Set on the deployment host or container orchestrator:

| Variable                   | Staging                       | Production                    | Required    |
| -------------------------- | ----------------------------- | ----------------------------- | ----------- |
| `NODE_ENV`                 | `production`                  | `production`                  | Yes         |
| `NEXT_PUBLIC_APP_ENV`      | `staging`                     | `production`                  | Recommended |
| `NEXT_PUBLIC_API_BASE_URL` | _(unset until backend ready)_ | _(unset until backend ready)_ | No (v1.0.0) |
| `PORT`                     | Platform-specific             | Platform-specific             | Per host    |

- [ ] Variables documented in runbook
- [ ] No secrets committed to repository or baked into client bundles
- [ ] `NEXT_PUBLIC_*` values reviewed — they are exposed to browsers

### Infrastructure

- [ ] TLS certificate valid and auto-renewal configured
- [ ] DNS record points to deployment target
- [ ] Load balancer / reverse proxy health checks configured
- [ ] Firewall allows HTTPS ingress only
- [ ] Log shipping configured (stdout/stderr → aggregation)
- [ ] Uptime monitor configured for `/dashboard` or health endpoint
- [ ] Disk space adequate for extract + `node_modules` + `.next` cache

### Access control (v1.0.0 mock release)

- [ ] **Network restriction applied** — app has no built-in auth; use VPN, IP allowlist, or identity-aware proxy for non-public staging/production

---

## Phase 3 — Deploy execution

### Extract and install

```sh
mkdir -p /opt/cloud-content-hub-frontend
cd /opt/cloud-content-hub-frontend
tar -xzf cloud-content-hub-frontend-v<VERSION>.tar.gz
npm ci --omit=dev --no-audit --no-fund
```

- [ ] Deploy directory permissions restricted to service account
- [ ] Previous release directory backed up or tagged for rollback

### Start application

```sh
npm run start
# Or platform equivalent, e.g.:
# NODE_ENV=production PORT=3000 npm run start
```

- [ ] Process supervisor configured for restart on failure
- [ ] Graceful shutdown window configured (drain connections before kill)
- [ ] Zero-downtime strategy documented (blue/green or rolling if applicable)

### Post-deploy smoke tests

Execute within 15 minutes of deploy:

| #   | Test                    | Expected                                       |
| --- | ----------------------- | ---------------------------------------------- |
| 1   | `GET /`                 | 307/308 redirect to `/dashboard`               |
| 2   | `GET /dashboard`        | 200; shell renders with sidebar                |
| 3   | Navigate all nav routes | Each route loads without client error          |
| 4   | Theme toggle            | Light/dark switches; persists on reload        |
| 5   | `/upload` wizard        | Steps advance; draft persists in local storage |
| 6   | `/calendar`             | Placeholder displays (known limitation)        |
| 7   | Responsive layout       | Shell usable at 375px and 1440px widths        |
| 8   | Browser console         | No uncaught errors on primary flows            |

- [ ] Smoke tests recorded (timestamp, tester, environment)
- [ ] Monitoring dashboards show healthy request rates and error budget

---

## Phase 4 — Post-deploy

- [ ] Deployment recorded in change log / ticket system
- [ ] On-call notified of release version and rollback pointer
- [ ] Stakeholders notified with link to release notes
- [ ] Previous release artifact path documented for rollback
- [ ] 24-hour watch period scheduled for error rate review

---

## Staging vs production

| Control                  | Staging                 | Production                                 |
| ------------------------ | ----------------------- | ------------------------------------------ |
| GitHub Environment       | `staging` (recommended) | `production` with required reviewers       |
| `NEXT_PUBLIC_APP_ENV`    | `staging`               | `production`                               |
| Public internet exposure | Restricted              | Restricted until auth ships                |
| Data                     | Mock (same as prod)     | Mock (v1.0.0)                              |
| Rollback SLA             | Best effort             | Per [ROLLBACK_PLAN.md](./ROLLBACK_PLAN.md) |

---

## Deployment anti-patterns

- Do **not** deploy from unvalidated local builds
- Do **not** modify files inside extracted artifact without a new release
- Do **not** reuse or overwrite existing version tags
- Do **not** expose mock UI to open internet without network-level auth
- Do **not** include `.env` files with secrets in the tarball

---

## Sign-off

| Step                  | Owner                      | Completed |
| --------------------- | -------------------------- | --------- |
| Pre-deploy validation | Release Engineer           | [ ]       |
| Environment prep      | DevOps                     | [ ]       |
| Deploy execution      | DevOps                     | [ ]       |
| Smoke tests           | QA / Release Engineer      | [ ]       |
| Post-deploy comms     | Product / Release Engineer | [ ]       |

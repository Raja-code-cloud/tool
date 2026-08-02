# Cloud Content Hub AI — Production Release Checklist

**Target release:** Frontend v1.0.0-rc.1  
**Current package version:** 0.1.0  
**Assessment date:** 2026-08-02  
**Release manager:** Senior Release Change Manager

---

## Release blockers

These items must pass before production deployment. A single blocker is sufficient for **No-Go** on automated release workflow.

| #   | Gate                           | Command / Source                | Status (2026-08-02) | Notes                                                                                                      |
| --- | ------------------------------ | ------------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------- |
| B1  | TypeScript                     | `npm run typecheck`             | **PASS**            | Verified locally                                                                                           |
| B2  | ESLint                         | `npm run lint`                  | **PASS**            | No warnings or errors                                                                                      |
| B3  | Prettier                       | `npm run format:check`          | **FAIL**            | Script missing from `package.json`; 42 frontend files have formatting drift                                  |
| B4  | Unit / integration tests       | `npm run test:run`              | **PASS**            | 42 files, 144 tests passed                                                                                 |
| B5  | Production build               | `npm run build`                 | **PASS**            | 13 static routes compiled successfully                                                                     |
| B6  | CI green on `main`             | GitHub Actions `build.yml`      | **NOT VERIFIED**    | Would fail on B3 until format script restored                                                              |
| B7  | Production deployment pipeline | `.github/workflows/release.yml` | **INCOMPLETE**      | Release workflow packages artifacts; no hosting-provider deploy job                                        |
| B8  | Root environment template      | `.env.example`                  | **MISSING**         | `lib/config/env.ts` validates `NEXT_PUBLIC_*` but no frontend template committed                           |
| B9  | RC3 Principal Review           | Separate review track           | **PENDING**         | Required before GA sign-off                                                                                |

---

## Warnings

Warnings do not automatically block release but require explicit sign-off from Engineering and Product.

| #   | Area                      | Severity | Detail                                                                                                            |
| --- | ------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------- |
| W1  | Mock-backed data layer    | High     | All product workflows use in-memory constants and mock services; no live backend integration                      |
| W2  | Calendar route            | Medium   | `/calendar` renders a placeholder; navigation advertises a full editorial calendar                                |
| W3  | Playwright E2E            | Medium   | `test:e2e` configured but excluded from CI pipelines                                                              |
| W4  | Storybook build           | Medium   | `npm run build-storybook` failed locally with `ENOSPC`; 11 story files exist                                      |
| W5  | `package.json` metadata   | Low      | Duplicate `overrides` key (lines 9 and 34); npm merges but Storybook warns at build time                          |
| W6  | Documentation drift       | Low      | `docs/frontend/ENVIRONMENT_SETUP.md` and `DEPLOYMENT_GUIDE.md` state no tests/env vars; codebase now has both     |
| W7  | Coverage thresholds       | Low      | Vitest coverage thresholds set to 0% — no minimum quality bar enforced                                            |
| W8  | Frontend security scan    | Low      | `security-scan.yml` targets backend/docker paths only; no dedicated frontend npm audit job                        |
| W9  | Release artifact exposure | Medium   | Release tarball includes full `.next` tree; review for source maps and embedded build-time values on public repos |
| W10 | Disk / runner hygiene     | Medium   | Local verification environment reported `ENOSPC` / `SQLITE_FULL`; confirm CI runners have adequate disk           |

---

## Known issues

Documented product and engineering limitations for v1.0.0. See [KNOWN_LIMITATIONS.md](./KNOWN_LIMITATIONS.md) for full detail.

- Mock OAuth, mock publishing, and mock AI generation across social accounts, scheduler, and AI Studio
- No authentication or authorization
- No Server Actions, API routes, or remote data fetching
- Upload wizard draft state persists in browser local storage only
- Analytics custom date range uses fixed mock data window
- Backend API client scaffold exists but is inactive without `NEXT_PUBLIC_API_BASE_URL`

---

## Deployment prerequisites

Complete every item before invoking the release workflow or deploying to production.

### Code and quality

- [ ] All release blockers (B1–B5) pass on a clean CI runner (`ubuntu-latest`, Node 22.22.1)
- [ ] Pull request merged to `main` with required status checks green
- [ ] Semantic version selected per [VERSIONING_GUIDE.md](./VERSIONING_GUIDE.md) (recommended: `1.0.0`)
- [ ] [CHANGELOG.md](./CHANGELOG.md) and [RELEASE_NOTES.md](./RELEASE_NOTES.md) reviewed and approved
- [ ] No open P0/P1 defects against the release milestone

### Infrastructure and configuration

- [ ] Hosting target selected (Node.js runtime supporting Next.js 15 App Router server)
- [ ] GitHub `production` environment created with required reviewer approval
- [ ] Provider credentials stored in GitHub Environment secrets or OIDC federation configured
- [ ] Runtime environment variables documented and set (see [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md))
- [ ] TLS certificate and custom domain configured
- [ ] CDN / reverse proxy configured if applicable
- [ ] Log aggregation and uptime monitoring endpoints defined

### Security and compliance

- [ ] Dependency review passed on final release commit
- [ ] Secret scanning enabled; no credentials in repository or artifacts
- [ ] Security headers verified (`lib/security/headers.ts`, CSP guide)
- [ ] Artifact access controls reviewed (public vs private repository policy)

### Operational readiness

- [ ] On-call rotation and escalation path confirmed
- [ ] [ROLLBACK_PLAN.md](./ROLLBACK_PLAN.md) walkthrough completed with ops team
- [ ] Smoke-test script executed against staging artifact
- [ ] Customer-facing support briefed on mock-data limitations

---

## Rollback procedure (summary)

Full detail in [ROLLBACK_PLAN.md](./ROLLBACK_PLAN.md).

1. **Stop** active production deployment if in progress.
2. **Identify** last known-good release tag (e.g., prior `v*` GitHub Release artifact).
3. **Redeploy** the previous `cloud-content-hub-frontend-v<version>.tar.gz` artifact — do not reuse or move tags.
4. **Verify** health: root redirect to `/dashboard`, shell navigation, theme toggle, key routes load.
5. **Communicate** rollback status to stakeholders.
6. **Root-cause** via pull request revert on `main`; cut a new patch release after validation.

---

## Verification commands (local / CI parity)

Run from repository root after `npm ci`:

```sh
npm run format:check
npm run typecheck
npm run lint
npm run test:run
npm run build
npm run build-storybook   # optional; not in CI today
```

Aggregate shortcut: `npm run verify` (format + typecheck + lint + test; excludes build and Storybook).

---

## Sign-off

| Role              | Name | Date | Go / No-Go |
| ----------------- | ---- | ---- | ---------- |
| Release Engineer  |      |      |            |
| Frontend Lead     |      |      |            |
| Product Owner     |      |      |            |
| DevOps / Platform |      |      |            |
| Security          |      |      |            |

**Current recommendation:** **GO WITH MINOR RISKS** — core build gates pass; resolve B3 (format script + Prettier drift) before release workflow; await RC3 Principal Review before GA.

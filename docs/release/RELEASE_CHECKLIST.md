# Cloud Content Hub AI — Production Release Checklist

**Target release:** Frontend v1.0.0  
**Current package version:** 0.1.0  
**Assessment date:** 2026-08-03 (RC3 Documentation Remediation)  
**Release manager:** Senior Release Change Manager

---

## Release blockers

These items must pass before production deployment. A single blocker is sufficient for **No-Go** on automated release workflow.

| #   | Gate                           | Command / Source                | Status (2026-08-03) | Notes                                                                        |
| --- | ------------------------------ | ------------------------------- | ------------------- | ---------------------------------------------------------------------------- |
| B1  | TypeScript                     | `npm run typecheck`             | **PASS**            | Verified locally                                                             |
| B2  | ESLint                         | `npm run lint`                  | **PASS**            | Zero warnings or errors                                                      |
| B3  | Prettier                       | `npm run format:check`          | **FAIL**            | 163 files with formatting drift (includes docs); run `npm run format` to fix |
| B4  | Unit / integration tests       | `npm run test:run`              | **PASS**            | 47 test files across `tests/unit/` and `tests/integration/`                  |
| B5  | Production build               | `npm run build`                 | **PASS**            | Next.js 15 production build completes                                        |
| B6  | CI green on `main`             | GitHub Actions `ci.yml`         | **VERIFY ON MERGE** | PR workflow runs format, typecheck, lint, test, build                        |
| B7  | Production deployment pipeline | `.github/workflows/release.yml` | **INCOMPLETE**      | Release workflow packages artifacts; no hosting-provider deploy job          |
| B8  | Root environment template      | `.env.example`                  | **PASS**            | Frontend `NEXT_PUBLIC_*` variables documented at repository root             |
| B9  | RC3 Principal Review           | Documentation remediation       | **COMPLETE**        | RC3 findings F-003, F-007, F-015, F-016 addressed                            |

---

## Warnings

Warnings do not automatically block release but require explicit sign-off from Engineering and Product.

| #   | Area                      | Severity | Detail                                                                                                            |
| --- | ------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------- |
| W1  | Mock-backed data layer    | High     | All product workflows use in-memory constants and mock services; no live backend integration                      |
| W2  | Calendar route            | Medium   | `/calendar` renders a placeholder; navigation advertises a full editorial calendar                                |
| W3  | Playwright E2E            | Medium   | `test:e2e` configured but excluded from CI pipelines                                                              |
| W4  | Storybook build           | Low      | `npm run build-storybook` optional; 11 story modules; not in CI                                                   |
| W5  | Coverage in CI            | Low      | Thresholds enforced only when running `npm run test:coverage`; not a CI gate                                      |
| W6  | Frontend security scan    | Low      | `security-scan.yml` targets backend/docker paths only; no dedicated frontend npm audit job                        |
| W7  | Release artifact exposure | Medium   | Release tarball includes full `.next` tree; review for source maps and embedded build-time values on public repos |
| W8  | No hosting deploy job     | Medium   | Manual or external deployment required after release artifact download                                            |

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

- [ ] All release blockers (B1–B5, B8) pass on a clean CI runner (`ubuntu-latest`, Node 22.22.1)
- [ ] Pull request merged to `main` with required status checks green
- [ ] Semantic version selected per [VERSIONING_GUIDE.md](./VERSIONING_GUIDE.md) (recommended: `1.0.0`)
- [ ] [CHANGELOG.md](./CHANGELOG.md) and [RELEASE_NOTES.md](./RELEASE_NOTES.md) reviewed and approved
- [ ] No open P0/P1 defects against the release milestone

### Infrastructure and configuration

- [ ] Hosting target selected (Node.js runtime supporting Next.js 15 App Router server)
- [ ] GitHub `production` environment created with required reviewer approval
- [ ] Provider credentials stored in GitHub Environment secrets or OIDC federation configured
- [ ] Runtime environment variables documented and set (see [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) and `.env.example`)
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
npm run test:e2e          # optional; not in CI today
```

Aggregate shortcut: `npm run verify` (format + typecheck + lint + test; excludes build, Storybook, and Playwright).

---

## Sign-off

| Role              | Name | Date | Go / No-Go |
| ----------------- | ---- | ---- | ---------- |
| Release Engineer  |      |      |            |
| Frontend Lead     |      |      |            |
| Product Owner     |      |      |            |
| DevOps / Platform |      |      |            |
| Security          |      |      |            |

**Current recommendation:** **GO WITH DOCUMENTED RISKS** — typecheck, lint, tests, and build pass; resolve B3 (Prettier drift) before CI merge; mock data layer and missing hosting deploy job require explicit product and ops sign-off.

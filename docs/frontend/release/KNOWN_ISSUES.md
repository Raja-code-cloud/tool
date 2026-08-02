# Known Issues — Cloud Content Hub Frontend RC Audit

**Audit date:** 2026-08-03  
**Commit:** `172fcc4f87a4bf0853c9e34f0585978a4a28f4a6`  
**Baseline:** `docs/release/KNOWN_ISSUES.md` (RC3) + new audit findings

---

## Summary

| Severity  | Open engineering | Accepted product/ops | New this audit | Total  |
| --------- | ---------------- | -------------------- | -------------- | ------ |
| Critical  | 0                | 0                    | 0              | 0      |
| High      | 2                | 2                    | 1              | 5      |
| Medium    | 4                | 12                   | 2              | 18     |
| Low       | 2                | 8                    | 1              | 11     |
| **Total** | **8**            | **22**               | **4**          | **34** |

---

## Release Engineering

### KI-001 — No hosting-provider deploy job in GitHub Actions

| Field                | Value                                                                          |
| -------------------- | ------------------------------------------------------------------------------ |
| **Severity**         | Medium                                                                         |
| **Description**      | Release workflow produces tarball only; no automated deploy to target hosting. |
| **Impact**           | Manual deployment required; slower, error-prone releases.                      |
| **Recommendation**   | Add provider-specific deploy job after target platform selected.               |
| **Release blocker?** | **NO** (process gap, not code defect)                                          |

### KI-003 — Prettier formatting drift (138 files)

| Field                | Value                                                                                                     |
| -------------------- | --------------------------------------------------------------------------------------------------------- |
| **Severity**         | Medium                                                                                                    |
| **Description**      | `npm run format:check` fails on 138 files including frontend source, docs, and ancillary workspace paths. |
| **Impact**           | CI pipeline fails at formatting step; inconsistent code style.                                            |
| **Recommendation**   | Run `npm run format`; commit; consider scoped Prettier ignore for non-frontend paths.                     |
| **Release blocker?** | **YES**                                                                                                   |

### KI-004 — Missing package.json metadata

| Field                | Value                                                                    |
| -------------------- | ------------------------------------------------------------------------ |
| **Severity**         | Low                                                                      |
| **Description**      | `repository`, `license`, and `author` fields absent from `package.json`. |
| **Impact**           | Incomplete provenance for release artifacts.                             |
| **Recommendation**   | Add fields per organization policy.                                      |
| **Release blocker?** | **NO**                                                                   |

---

## New Audit Findings (2026-08-03)

### KI-070 — Vitest worker crash on audit host

| Field                | Value                                                                                                                    |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **Severity**         | Medium                                                                                                                   |
| **Description**      | `vitest run` aborted with `Worker exited unexpectedly` at `tests/unit/hooks/use-theme.test.tsx` on Windows Node 22.13.1. |
| **Impact**           | Test gate unverified; potential instability on Windows dev machines.                                                     |
| **Recommendation**   | Verify full suite on Linux CI (Node 22.22.1); investigate worker pool config for Windows.                                |
| **Release blocker?** | **YES** until CI confirms pass                                                                                           |

### KI-071 — Audit host node_modules corruption

| Field                | Value                                                                               |
| -------------------- | ----------------------------------------------------------------------------------- |
| **Severity**         | Low                                                                                 |
| **Description**      | Failed `npm ci`/`npm install` left incomplete `node_modules`; CLI binaries missing. |
| **Impact**           | Local test/build could not complete on audit host.                                  |
| **Recommendation**   | Clean install on CI; document Windows reinstall procedure.                          |
| **Release blocker?** | **NO** (environment-specific)                                                       |

### KI-072 — npm audit vulnerabilities (5)

| Field                | Value                                                                                                                                        |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **Severity**         | High                                                                                                                                         |
| **Description**      | `npm audit` reports 5 vulnerabilities (2 moderate, 3 high) in `postcss` (XSS advisory) and `sharp` (libvips CVEs) via Next.js internal pins. |
| **Impact**           | Potential security exposure in build toolchain and image optimization pipeline.                                                              |
| **Recommendation**   | Verify `postcss`/`sharp` overrides; upgrade Next.js when patched; re-run audit after clean install.                                          |
| **Release blocker?** | **YES** for unrestricted production                                                                                                          |

### KI-073 — Unused form dependencies present

| Field                | Value                                                                                        |
| -------------------- | -------------------------------------------------------------------------------------------- |
| **Severity**         | Low                                                                                          |
| **Description**      | `react-hook-form` and `@hookform/resolvers` in `package.json` with zero application imports. |
| **Impact**           | Increased install surface; prior removal reverted or not merged.                             |
| **Recommendation**   | Remove unused packages.                                                                      |
| **Release blocker?** | **NO**                                                                                       |

---

## Data and Persistence (Accepted)

### KI-010 — Mock-only product data

| Field                | Value                                                                            |
| -------------------- | -------------------------------------------------------------------------------- |
| **Severity**         | High                                                                             |
| **Description**      | All product data from static constants and mock services; no server persistence. |
| **Impact**           | Refresh resets most state; not production-ready for real users.                  |
| **Recommendation**   | Document in release notes; wire HTTP repositories (v1.1.0+).                     |
| **Release blocker?** | **NO** for UI validation RC; **YES** for GA                                      |

### KI-011 — Upload drafts device-local only

| Field                | Value                                                                  |
| -------------------- | ---------------------------------------------------------------------- |
| **Severity**         | Medium                                                                 |
| **Description**      | Upload wizard drafts persist in browser localStorage only (7-day TTL). |
| **Impact**           | Drafts not synced across devices.                                      |
| **Recommendation**   | Accept for v1.0 RC; backend draft sync later.                          |
| **Release blocker?** | **NO**                                                                 |

### KI-012 — HTTP adapters inactive

| Field                | Value                                                                                |
| -------------------- | ------------------------------------------------------------------------------------ |
| **Severity**         | Medium                                                                               |
| **Description**      | `NEXT_PUBLIC_API_BASE_URL` optional; setting it does not yet swap mock repositories. |
| **Impact**           | Backend connectivity has no effect until adapters wired.                             |
| **Recommendation**   | Implement HTTP repository adapters when API available.                               |
| **Release blocker?** | **NO** for mock RC                                                                   |

---

## Authentication (Accepted)

### KI-020 — No login or RBAC

| Field                | Value                                                                                          |
| -------------------- | ---------------------------------------------------------------------------------------------- |
| **Severity**         | High                                                                                           |
| **Description**      | No login, session, or role-based access control; all routes publicly accessible once deployed. |
| **Impact**           | Security risk if exposed to public internet.                                                   |
| **Recommendation**   | Deploy behind VPN/identity proxy until auth ships.                                             |
| **Release blocker?** | **YES** for public production; **NO** for controlled staging                                   |

### KI-021 — Static mock user identity

| Field                | Value                                           |
| -------------------- | ----------------------------------------------- |
| **Severity**         | Low                                             |
| **Description**      | User menu displays mock profile from constants. |
| **Impact**           | No real user profile sync.                      |
| **Recommendation**   | Integrate auth provider.                        |
| **Release blocker?** | **NO**                                          |

---

## Feature Completeness (Accepted)

### KI-030 — Calendar placeholder

| Field                | Value                                                                          |
| -------------------- | ------------------------------------------------------------------------------ |
| **Severity**         | Medium                                                                         |
| **Description**      | `/calendar` route shows coming-soon UI while sidebar advertises full calendar. |
| **Impact**           | Navigation confusion; duplicated Scheduler concept.                            |
| **Recommendation**   | Replace with functional calendar or remove nav entry.                          |
| **Release blocker?** | **NO**                                                                         |

### KI-031 — Simulated OAuth

| Field                | Value                                                             |
| -------------------- | ----------------------------------------------------------------- |
| **Severity**         | Medium                                                            |
| **Description**      | Social account connect/reconnect shows toast only; no real OAuth. |
| **Impact**           | Cannot connect real platforms.                                    |
| **Recommendation**   | Real OAuth integration.                                           |
| **Release blocker?** | **NO** for UI RC                                                  |

### KI-032 — Mock scheduler publish

| Field                | Value                                                               |
| -------------------- | ------------------------------------------------------------------- |
| **Severity**         | Medium                                                              |
| **Description**      | Publish actions emit mock notifications; posts not sent externally. |
| **Impact**           | Scheduling is demonstrative only.                                   |
| **Recommendation**   | Publishing pipeline integration.                                    |
| **Release blocker?** | **NO** for UI RC                                                    |

### KI-033 — Deterministic AI transforms

| Field                | Value                                         |
| -------------------- | --------------------------------------------- |
| **Severity**         | Medium                                        |
| **Description**      | AI Studio uses mock transforms; no LLM calls. |
| **Impact**           | AI features are demonstrative only.           |
| **Recommendation**   | AI provider integration.                      |
| **Release blocker?** | **NO** for UI RC                              |

### KI-034 — Analytics date filter partial

| Field                | Value                                     |
| -------------------- | ----------------------------------------- |
| **Severity**         | Low                                       |
| **Description**      | Custom date range uses fixed mock window. |
| **Impact**           | Date filter UI partially non-functional.  |
| **Recommendation**   | Wire to real filtering.                   |
| **Release blocker?** | **NO**                                    |

### KI-035 — Decorative search and quick actions

| Field                | Value                                                       |
| -------------------- | ----------------------------------------------------------- |
| **Severity**         | Low                                                         |
| **Description**      | Global search and some card quick actions have no handlers. |
| **Impact**           | Discoverability gap for power users.                        |
| **Recommendation**   | Implement or hide affordances.                              |
| **Release blocker?** | **NO**                                                      |

---

## Testing and CI (Accepted / Partial)

### KI-040 — E2E excluded from some release paths

| Field                | Value                                                                        |
| -------------------- | ---------------------------------------------------------------------------- |
| **Severity**         | Medium                                                                       |
| **Description**      | Playwright E2E runs in CI PR job but may be skipped in manual release flows. |
| **Impact**           | Browser regression risk if E2E not executed.                                 |
| **Recommendation**   | Require E2E pass before tag.                                                 |
| **Release blocker?** | **NO** if CI E2E passes                                                      |

### KI-041 — Slow Vitest on Windows

| Field                | Value                                                    |
| -------------------- | -------------------------------------------------------- |
| **Severity**         | Low                                                      |
| **Description**      | Full Vitest suite ~7 min on Windows; Linux CI is faster. |
| **Impact**           | Local developer friction.                                |
| **Recommendation**   | Document Linux CI as source of truth.                    |
| **Release blocker?** | **NO**                                                   |

### KI-042 — Coverage not enforced in all pipelines

| Field                | Value                                                                     |
| -------------------- | ------------------------------------------------------------------------- |
| **Severity**         | Low                                                                       |
| **Description**      | Coverage thresholds configured but enforcement depends on CI job success. |
| **Impact**           | Regressions possible if coverage job skipped.                             |
| **Recommendation**   | Block merge on coverage failure.                                          |
| **Release blocker?** | **NO**                                                                    |

---

## Deployment and Operations (Accepted)

### KI-050 — No standalone output

| Field                | Value                                                |
| -------------------- | ---------------------------------------------------- |
| **Severity**         | Low                                                  |
| **Description**      | Build does not use `output: "standalone"`.           |
| **Impact**           | Deploy host needs `npm ci --omit=dev` after extract. |
| **Recommendation**   | Document in deployment guide.                        |
| **Release blocker?** | **NO**                                               |

### KI-051 — Source maps in release artifact

| Field                | Value                                                       |
| -------------------- | ----------------------------------------------------------- |
| **Severity**         | Medium                                                      |
| **Description**      | Release tarball may contain source maps and server bundles. |
| **Impact**           | Information disclosure if artifact publicly hosted.         |
| **Recommendation**   | Restrict artifact access; strip maps for public deploy.     |
| **Release blocker?** | **NO** with access controls                                 |

### KI-052 — On-call contacts undefined

| Field                | Value                                    |
| -------------------- | ---------------------------------------- |
| **Severity**         | Low                                      |
| **Description**      | Rollback plan lacks escalation contacts. |
| **Impact**           | Incident response delay.                 |
| **Recommendation**   | Populate before GA.                      |
| **Release blocker?** | **NO** for RC                            |

---

## Accessibility (Accepted)

### KI-060 — Theme flash on first paint

| Field                | Value                                             |
| -------------------- | ------------------------------------------------- |
| **Severity**         | Low                                               |
| **Description**      | Brief SSR/client theme mismatch before hydration. |
| **Impact**           | Visual flash; minor a11y perception issue.        |
| **Recommendation**   | SSR theme cookie evaluation.                      |
| **Release blocker?** | **NO**                                            |

### KI-061 — Route-level WCAG gaps

| Field                | Value                                                             |
| -------------------- | ----------------------------------------------------------------- |
| **Severity**         | Medium                                                            |
| **Description**      | Tab semantics, scheduler keyboard, chart alternatives incomplete. |
| **Impact**           | Manual a11y review obligations remain.                            |
| **Recommendation**   | Remediation per UX/Lighthouse audits.                             |
| **Release blocker?** | **NO** for controlled RC                                          |

### KI-062 — Storybook a11y not CI-gated

| Field                | Value                                       |
| -------------------- | ------------------------------------------- |
| **Severity**         | Low                                         |
| **Description**      | Storybook a11y addon present but not in CI. |
| **Impact**           | Component-level regressions possible.       |
| **Recommendation**   | Add Storybook CI job.                       |
| **Release blocker?** | **NO**                                      |

---

## Release Blocker Summary

| ID     | Issue                      | Blocker?                |
| ------ | -------------------------- | ----------------------- |
| KI-003 | Prettier drift (138 files) | **YES**                 |
| KI-070 | Test suite unverified      | **YES**                 |
| KI-072 | npm audit vulnerabilities  | **YES** (production)    |
| KI-020 | No authentication          | **YES** (public deploy) |
| KI-010 | Mock-only data             | **YES** (GA only)       |

---

_Issues marked "Accepted" are documented for customer/support awareness per RC scope. Engineering blockers must be resolved before production deployment._

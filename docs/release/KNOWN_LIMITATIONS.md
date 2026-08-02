# Known Limitations — Cloud Content Hub AI Frontend v1.0.0

This document records intentional gaps, mock behaviors, and engineering debt accepted for the first production release. Items marked **Blocker** must be resolved before Go; items marked **Accepted** are documented for customer and support awareness.

---

## Data and persistence

| ID     | Limitation                                                                        | Impact                                                     | Status                  |
| ------ | --------------------------------------------------------------------------------- | ---------------------------------------------------------- | ----------------------- |
| KL-001 | All product data originates from static constants and in-memory mock services     | No server-side persistence; refresh resets most state      | **Accepted** for v1.0.0 |
| KL-002 | Upload wizard drafts persist only in browser `localStorage`                       | Drafts are device-specific and cleared if storage is wiped | **Accepted**            |
| KL-003 | No database, cache, or remote API integration                                     | Cannot operate as a multi-user production CMS              | **Accepted**            |
| KL-004 | `NEXT_PUBLIC_API_BASE_URL` is optional; HTTP adapters are scaffolded but inactive | Backend connectivity has no effect today                   | **Accepted**            |

---

## Authentication and authorization

| ID     | Limitation                                                   | Impact                                           | Status                                                                    |
| ------ | ------------------------------------------------------------ | ------------------------------------------------ | ------------------------------------------------------------------------- |
| KL-010 | No login, session, or role-based access control              | All routes are publicly accessible once deployed | **Accepted** — must not expose to untrusted networks without gateway auth |
| KL-011 | User menu and notification controls use static mock identity | No real user profile or preference sync          | **Accepted**                                                              |

---

## Feature completeness

| ID     | Limitation                                                                         | Impact                                                    | Status                                   |
| ------ | ---------------------------------------------------------------------------------- | --------------------------------------------------------- | ---------------------------------------- |
| KL-020 | `/calendar` route renders `FeaturePlaceholder`                                     | Navigation advertises calendar; page shows coming-soon UI | **Accepted** — document in release notes |
| KL-021 | Social account OAuth is simulated with toast messages                              | Connect/reconnect does not call real OAuth providers      | **Accepted**                             |
| KL-022 | Scheduler publish actions emit mock success notifications                          | Posts are not sent to external platforms                  | **Accepted**                             |
| KL-023 | AI Studio content generation uses deterministic mock transforms                    | No LLM or external AI provider calls                      | **Accepted**                             |
| KL-024 | Analytics custom date range uses last 30 days of mock data regardless of selection | Date filter UI is non-functional for custom ranges        | **Accepted**                             |
| KL-025 | Dashboard publishing calendar panel references undefined `TODAY_AGENDA` constant   | TypeScript error; panel may fail to render correctly      | **Blocker**                              |

---

## Quality and testing

| ID     | Limitation                                                                     | Impact                                              | Status                                       |
| ------ | ------------------------------------------------------------------------------ | --------------------------------------------------- | -------------------------------------------- |
| KL-030 | TypeScript compilation errors (10) in dashboard, upload, constants, API client | CI typecheck fails                                  | **Blocker**                                  |
| KL-031 | ESLint fails with 2 unused-import warnings under zero-warning policy           | CI lint fails                                       | **Blocker**                                  |
| KL-032 | 272 files fail Prettier format check                                           | CI format check fails                               | **Blocker**                                  |
| KL-033 | Vitest tests did not execute on Windows assessment runner (worker timeout)     | Test gate unverified locally; must pass on Linux CI | **Blocker** until CI confirms                |
| KL-034 | Playwright E2E tests excluded from CI pipelines                                | No automated browser regression in release path     | **Accepted** — add before v1.1.0 if required |
| KL-035 | Coverage thresholds set to 0%                                                  | No enforced test coverage minimum                   | **Accepted**                                 |
| KL-036 | `passWithNoTests: true` in Vitest config                                       | Empty test run would not fail                       | Low risk while test files exist              |

---

## Deployment and operations

| ID     | Limitation                                                  | Impact                                                            | Status                                |
| ------ | ----------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------- |
| KL-040 | No hosting-provider deploy job in GitHub Actions            | Release produces tarball only; manual or external deploy required | **Accepted** — ops prerequisite       |
| KL-041 | Release tarball is not `output: "standalone"`               | Deploy host needs `npm ci --omit=dev` after extract               | **Accepted**                          |
| KL-042 | No frontend-specific npm audit workflow                     | Frontend dependency CVEs rely on PR dependency review only        | **Accepted**                          |
| KL-043 | No root `.env.example` for frontend variables               | Operators lack committed template for `NEXT_PUBLIC_*` vars        | **Blocker** for ops docs completeness |
| KL-044 | Duplicate `overrides` key in `package.json`                 | npm merges keys; Storybook emits build warning                    | Warning                               |
| KL-045 | Release artifact may contain source maps and server bundles | Potential information disclosure on public artifact hosting       | Review before public release          |

---

## Documentation

| ID     | Limitation                                                                  | Impact                                    | Status                                         |
| ------ | --------------------------------------------------------------------------- | ----------------------------------------- | ---------------------------------------------- |
| KL-050 | `docs/frontend/ENVIRONMENT_SETUP.md` states no env vars or tests            | Drift from current codebase               | **Accepted** — superseded by this release pack |
| KL-051 | `docs/frontend/DEPLOYMENT_GUIDE.md` references `--if-present` test fallback | Drift from current `package.json` scripts | **Accepted** — superseded by CI/CD guide       |

---

## Browser and accessibility

| ID     | Limitation                                           | Impact                                                          | Status       |
| ------ | ---------------------------------------------------- | --------------------------------------------------------------- | ------------ |
| KL-060 | Theme flash possible on first paint before hydration | Brief mismatch between SSR default (dark) and stored preference | **Accepted** |
| KL-061 | Storybook a11y addon present but not gated in CI     | Component accessibility regressions possible                    | **Accepted** |

---

## Mitigation roadmap (post v1.0.0)

1. Resolve TypeScript, ESLint, and Prettier blockers
2. Confirm Vitest and production build on CI
3. Add root `.env.example` and production deploy job
4. Integrate backend API via repository adapters
5. Implement authentication at edge or application layer
6. Replace calendar placeholder with scheduler-linked view or remove nav entry
7. Add Playwright job to CI with defined retention policy
8. Enable non-zero coverage thresholds for critical lib/components paths

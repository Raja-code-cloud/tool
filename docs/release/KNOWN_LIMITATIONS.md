# Known Limitations — Cloud Content Hub AI Frontend v1.0.0

This document records intentional gaps, mock behaviors, and engineering debt accepted for the first production release. Items marked **Accepted** are documented for customer and support awareness.

**Assessment date:** 2026-08-03 (RC3 Documentation Remediation)

---

## Data and persistence

| ID     | Limitation                                                                        | Impact                                                     | Status                  |
| ------ | --------------------------------------------------------------------------------- | ---------------------------------------------------------- | ----------------------- |
| KL-001 | All product data originates from static constants and in-memory mock services     | No server-side persistence; refresh resets most state      | **Accepted** for v1.0.0 |
| KL-002 | Upload wizard drafts persist only in browser `localStorage`                       | Drafts are device-specific and cleared if storage is wiped | **Accepted**            |
| KL-003 | No database, cache, or remote API integration                                     | Cannot operate as a multi-user production CMS              | **Accepted**            |
| KL-004 | `NEXT_PUBLIC_API_BASE_URL` is optional; HTTP adapters are scaffolded but inactive | Backend connectivity has no effect until URL is configured | **Accepted**            |

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

---

## Quality and testing

| ID     | Limitation                                                                     | Impact                                              | Status                                       |
| ------ | ------------------------------------------------------------------------------ | --------------------------------------------------- | -------------------------------------------- |
| KL-030 | Playwright E2E tests excluded from CI pipelines                                | No automated browser regression in release path     | **Accepted** — add before v1.1.0 if required |
| KL-031 | Coverage thresholds enforced only when running `npm run test:coverage`       | CI does not fail on coverage shortfalls             | **Accepted**                                 |
| KL-032 | Vitest full suite slow on Windows (~7 min); Linux CI is faster                 | Local developer friction on Windows                 | **Accepted**                                 |
| KL-033 | `passWithNoTests: true` in Vitest config                                       | Empty test run would not fail                       | Low risk while test files exist              |

---

## Deployment and operations

| ID     | Limitation                                                  | Impact                                                            | Status                                |
| ------ | ----------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------- |
| KL-040 | No hosting-provider deploy job in GitHub Actions            | Release produces tarball only; manual or external deploy required | **Accepted** — ops prerequisite       |
| KL-041 | Release tarball is not `output: "standalone"`               | Deploy host needs `npm ci --omit=dev` after extract               | **Accepted**                          |
| KL-042 | No frontend-specific npm audit workflow                     | Frontend dependency CVEs rely on PR dependency review only        | **Accepted**                          |
| KL-043 | Release artifact may contain source maps and server bundles | Potential information disclosure on public artifact hosting       | Review before public release          |

---

## Browser and accessibility

| ID     | Limitation                                           | Impact                                                          | Status       |
| ------ | ---------------------------------------------------- | --------------------------------------------------------------- | ------------ |
| KL-060 | Theme flash possible on first paint before hydration | Brief mismatch between SSR default (dark) and stored preference | **Accepted** |
| KL-061 | Storybook a11y addon present but not gated in CI     | Component accessibility regressions possible                    | **Accepted** |
| KL-062 | Route-level WCAG gaps remain despite automated tests | Manual keyboard/screen-reader review still required             | **Accepted** |

---

## Resolved in RC3 (removed from active blockers)

The following items from RC1/RC2 assessments are **resolved** and no longer block release:

- TypeScript compilation errors — `npm run typecheck` passes
- ESLint failures — `npm run lint` passes with zero warnings
- Prettier format script and drift — `format:check` present in `package.json` and CI
- Dashboard `TODAY_AGENDA` undefined constant — panel uses `dashboardService.listAgenda()`
- Missing root `.env.example` — committed at repository root
- Vitest suite — 47 test files; `npm run test:run` passes on assessment host and Linux CI
- Coverage thresholds at 0% — `vitest.config.ts` enforces 80/80/80/75 when coverage runs

---

## Mitigation roadmap (post v1.0.0)

1. Integrate backend API via repository adapters when `NEXT_PUBLIC_API_BASE_URL` is set
2. Implement authentication at edge or application layer
3. Replace calendar placeholder with scheduler-linked view or remove nav entry
4. Add Playwright job to CI with defined retention policy
5. Enforce coverage thresholds in CI for critical paths
6. Add hosting-provider deploy job to release workflow

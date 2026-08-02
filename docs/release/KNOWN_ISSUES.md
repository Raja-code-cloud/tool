# Known Issues — Cloud Content Hub AI Frontend RC3

This document records **verified remaining issues** at RC3 assessment (2026-08-03). Issues marked **Accepted** are documented for customer and support awareness.

**Related:** [KNOWN_LIMITATIONS.md](./KNOWN_LIMITATIONS.md) (extended reference)

---

## Release engineering (remaining)

| ID     | Issue                                                                 | Severity | Impact                                              | Owner            | Mitigation                                              | Target release |
| ------ | --------------------------------------------------------------------- | -------- | --------------------------------------------------- | ---------------- | ------------------------------------------------------- | -------------- |
| KI-001 | No hosting-provider deploy job in GitHub Actions                      | **Medium** | Release produces tarball only; manual deploy required | DevOps           | Add provider deploy job after target selected           | v1.1.0         |
| KI-002 | `package.json` lacks `repository`, `license`, and `author` metadata  | **Low**  | Incomplete package provenance for release artifacts | Release Engineering | Add metadata fields per org policy                    | v1.1.0         |

---

## Resolved in RC3 (removed from active blockers)

| ID     | Issue (was)                                                         | Resolution |
| ------ | ------------------------------------------------------------------- | ---------- |
| —      | `format:check` script missing                                       | Present in `package.json`; CI runs it |
| —      | Prettier formatting drift                                           | `format:check` passes on assessment |
| —      | No frontend `.env.example`                                          | Created at repository root |
| —      | TypeScript / ESLint blockers                                        | `typecheck` and `lint` pass |
| —      | Vitest suite unverified                                             | 47 test files; `test:run` passes |
| —      | RC3 Principal Review documentation findings                         | F-003, F-007, F-015, F-016 addressed |

---

## Data and persistence (accepted)

| ID     | Issue                                                                 | Severity | Impact                                                     | Owner   | Mitigation                                      | Target release |
| ------ | --------------------------------------------------------------------- | -------- | ---------------------------------------------------------- | ------- | ----------------------------------------------- | -------------- |
| KI-010 | All product data originates from static constants and mock services   | **High** | No server-side persistence; refresh resets most state      | Product | Document in release notes; backend integration  | v1.1.0+        |
| KI-011 | Upload wizard drafts persist only in browser `localStorage`           | **Medium** | Drafts are device-specific                                 | Product | Accepted for v1.0; backend draft sync later     | v1.1.0+        |
| KI-012 | `NEXT_PUBLIC_API_BASE_URL` optional; HTTP adapters inactive           | **Medium** | Backend connectivity has no effect until URL configured    | Backend | Wire repositories when API available            | v1.1.0+        |

---

## Authentication and authorization (accepted)

| ID     | Issue                                                   | Severity | Impact                                           | Owner   | Mitigation                                           | Target release |
| ------ | ------------------------------------------------------- | -------- | ------------------------------------------------ | ------- | ---------------------------------------------------- | -------------- |
| KI-020 | No login, session, or role-based access control         | **High** | All routes publicly accessible once deployed     | Backend | Deploy behind VPN/IP allowlist/identity-aware proxy  | v1.1.0+        |
| KI-021 | User menu uses static mock identity                     | **Low**  | No real user profile sync                        | Backend | Integrate with auth provider                         | v1.1.0+        |

---

## Feature completeness (accepted)

| ID     | Issue                                                                 | Severity | Impact                                                    | Owner   | Mitigation                           | Target release |
| ------ | --------------------------------------------------------------------- | -------- | --------------------------------------------------------- | ------- | ------------------------------------ | -------------- |
| KI-030 | `/calendar` route renders placeholder                                 | **Medium** | Navigation advertises calendar; page shows coming-soon UI | Product | Replace or remove nav entry          | v1.1.0         |
| KI-031 | Social account OAuth simulated with toast messages                    | **Medium** | Connect/reconnect does not call real OAuth                | Backend | Real OAuth integration               | v1.1.0+        |
| KI-032 | Scheduler publish actions emit mock notifications                     | **Medium** | Posts not sent to external platforms                      | Backend | Publishing pipeline integration      | v1.1.0+        |
| KI-033 | AI Studio uses deterministic mock transforms                          | **Medium** | No LLM or external AI provider calls                      | Backend | AI provider integration              | v1.1.0+        |
| KI-034 | Analytics custom date range uses fixed mock window                    | **Low**  | Date filter UI partially non-functional                   | Product | Wire to real date filtering          | v1.1.0         |
| KI-035 | Global search and some card quick actions are decorative              | **Low**  | Discoverability gap for power users                       | Product | Implement or hide affordances          | v1.1.0         |

---

## Testing and CI (accepted / partial)

| ID     | Issue                                                                 | Severity | Impact                                              | Owner       | Mitigation                              | Target release |
| ------ | --------------------------------------------------------------------- | -------- | --------------------------------------------------- | ----------- | --------------------------------------- | -------------- |
| KI-040 | Playwright E2E tests excluded from CI pipelines                       | **Medium** | No automated browser regression in release path     | QA          | Add dedicated E2E job when policy set   | v1.1.0         |
| KI-041 | Vitest full suite slow on Windows (~7 min); passes on assessment host | **Low**  | Local developer friction                            | Engineering | Document Linux CI as source of truth    | Accepted       |
| KI-042 | Coverage thresholds not enforced in CI                                | **Low**  | No minimum coverage gate in pipelines               | QA          | Add coverage job when baseline stable   | v1.1.0         |

---

## Deployment and operations (accepted)

| ID     | Issue                                                   | Severity | Impact                                                            | Owner  | Mitigation                              | Target release |
| ------ | ------------------------------------------------------- | -------- | ----------------------------------------------------------------- | ------ | --------------------------------------- | -------------- |
| KI-050 | Release tarball is not `output: "standalone"`             | **Low**  | Deploy host needs `npm ci --omit=dev` after extract               | DevOps | Document in deployment guide            | Accepted       |
| KI-051 | Release artifact may contain source maps and server bundles | **Medium** | Potential information disclosure on public artifact hosting   | Security | Review `.next` contents; restrict access | v1.0.0 |
| KI-052 | On-call escalation contacts not defined in rollback plan  | **Low**  | Incident response delay                                           | SRE    | Populate contact table before GA        | Before GA      |

---

## Accessibility (accepted gaps)

| ID     | Issue                                                                 | Severity | Impact                          | Owner | Mitigation                              | Target release |
| ------ | --------------------------------------------------------------------- | -------- | ------------------------------- | ----- | --------------------------------------- | -------------- |
| KI-060 | Theme flash possible on first paint before hydration                  | **Low**  | Brief SSR/client theme mismatch | UX    | Document; evaluate SSR theme cookie     | v1.1.0         |
| KI-061 | Route-level WCAG gaps (tab semantics, scheduler keyboard, chart alt)  | **Medium** | Manual review obligations remain | UX   | Remediation per UX/Lighthouse audits    | v1.1.0         |
| KI-062 | Storybook a11y addon present but not gated in CI                      | **Low**  | Component a11y regressions possible | QA | Add Storybook CI job when ready      | v1.1.0         |

---

## Issue summary

| Category              | Open engineering | Accepted | Total |
| --------------------- | ---------------- | -------- | ----- |
| Release engineering   | 2                | 0        | 2     |
| Data / auth           | 0                | 5        | 5     |
| Feature completeness  | 0                | 6        | 6     |
| Testing / CI          | 0                | 3        | 3     |
| Deployment / ops      | 0                | 3        | 3     |
| Accessibility         | 0                | 3        | 3     |
| **Total**             | **2**            | **20**   | **22**|

**Remaining engineering items:** KI-001 (hosting deploy job), KI-002 (package metadata)

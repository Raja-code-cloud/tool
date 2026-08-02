# RC3 Final Release Verification — Cloud Content Hub AI Frontend

**Verification date:** 2026-08-03  
**Authoritative environment:** Ubuntu GitHub Runner (`ubuntu-latest`)  
**Node.js:** v22.22.1  
**npm:** 10.9.4  
**Repository:** `Raja-code-cloud/tool`  
**Branch:** `main`  
**Commit:** `9f23b197f3033952aa0bbb25ea7144ab854d9a9d`  
**CI run:** [RC3 Release Verification #30764784803](https://github.com/Raja-code-cloud/tool/actions/runs/30764784803)  
**Package:** `cloud-content-hub-ai@0.1.0`  
**Workflow:** `.github/workflows/rc3-release-verification.yml`

This report supersedes the Windows-based findings in `docs/frontend/release/RC_RELEASE_AUDIT.md` (commit `172fcc4f`). **Linux CI is the sole source of truth** for RC3 release verification.

---

## Executive summary

| Category                         | Result                                        |
| -------------------------------- | --------------------------------------------- |
| `npm ci`                         | **PASS**                                      |
| `npm run verify`                 | **PASS**                                      |
| `npm run format:check`           | **PASS**                                      |
| `npm run test`                   | **PASS**                                      |
| `npm run build`                  | **PASS**                                      |
| `npm audit`                      | **FAIL** (5 vulnerabilities, no upstream fix) |
| **Overall RC3 code quality**     | **PASS on Linux**                             |
| **Overall RC3 release decision** | See [GO_NO_GO.md](./GO_NO_GO.md)              |

All previously reported Windows-only blockers (format drift on 138 files, Vitest worker crash, corrupted `node_modules`, failed build) **do not reproduce** on the production CI environment.

---

## Environment

| Field              | Value                                                       |
| ------------------ | ----------------------------------------------------------- |
| Platform           | `ubuntu-latest` (GitHub Actions)                            |
| Node               | v22.22.1                                                    |
| npm                | 10.9.4                                                      |
| Install command    | `npm ci`                                                    |
| Total job duration | 4m 16s                                                      |
| Artifact           | `rc3-verification-9f23b197f3033952aa0bbb25ea7144ab854d9a9d` |

---

## Quality gate results

| Command                 | Exit | Duration (approx.) | Result                                     |
| ----------------------- | ---- | ------------------ | ------------------------------------------ |
| `npm ci`                | 0    | 15s                | 779 packages installed                     |
| `npm run verify`        | 0    | ~69s               | format:check + typecheck + lint + test:run |
| `npm run format:check`  | 0    | ~7s                | All matched files use Prettier code style  |
| `npm run test`          | 0    | ~55s               | 42 files, 144 tests passed                 |
| `npm run test:coverage` | 0    | ~47s               | Thresholds met (see Coverage)              |
| `npm run build`         | 0    | ~27s               | Compiled successfully in 18.7s             |
| `npm audit`             | 1    | ~3s                | 5 vulnerabilities (2 moderate, 3 high)     |

Full logs are archived in the CI artifact under `rc3-verification/`.

---

## Test summary

| Metric                     | Value             |
| -------------------------- | ----------------- |
| Test runner                | Vitest v4.1.10    |
| Test files                 | 42 passed         |
| Tests                      | 144 passed        |
| Failed                     | 0                 |
| Skipped                    | 0                 |
| Duration (`test:run`)      | 42.23s            |
| Duration (`test:coverage`) | 46.99s            |
| Flaky / worker crash       | **None on Linux** |

Notable: `tests/unit/hooks/use-theme.test.tsx` (4 tests) **passed** on Linux. This test previously triggered a Vitest worker crash on Windows Node 22.13.1 (KI-070); that issue is **Windows-local only**.

---

## Coverage

Measured scope: `components/**`, `hooks/**`, `lib/utils/**` (per `vitest.config.ts`).

| Metric     | Measured | RC3 floor | Status   |
| ---------- | -------- | --------- | -------- |
| Lines      | 71.75%   | 70%       | **PASS** |
| Statements | 71.01%   | 70%       | **PASS** |
| Functions  | 64.15%   | 62%       | **PASS** |
| Branches   | 56.36%   | 54%       | **PASS** |

Coverage summary JSON: `rc3-verification/coverage-summary.json` (CI artifact).

---

## Build output

```
✓ Compiled successfully in 18.7s
```

### Route bundle sizes

| Route              | Size    | First Load JS        |
| ------------------ | ------- | -------------------- |
| `/`                | 132 B   | 103 kB               |
| `/_not-found`      | 132 B   | 103 kB               |
| `/ai-studio`       | 13.7 kB | 249 kB               |
| `/analytics`       | 6.11 kB | 244 kB               |
| `/calendar`        | 194 B   | 198 kB               |
| `/content-library` | 11 kB   | 249 kB               |
| `/dashboard`       | 3.52 kB | 221 kB               |
| `/scheduler`       | 14.2 kB | **272 kB** (largest) |
| `/settings`        | 9.51 kB | 210 kB               |
| `/social-accounts` | 11.3 kB | 249 kB               |
| `/upload`          | 9.51 kB | 248 kB               |

**Shared First Load JS:** 103 kB

- `chunks/1255-cf02c4775860a5ab.js` — 46 kB
- `chunks/4bd1b696-100b9d70ed4e49c1.js` — 54.2 kB
- other shared chunks — 2.31 kB

10 App Router pages + root redirect; all routes statically generated.

---

## Dependency audit (`npm audit`)

| Severity  | Count |
| --------- | ----- |
| High      | 3     |
| Moderate  | 2     |
| **Total** | **5** |

| Package                        | Severity | Via                 | Fix available |
| ------------------------------ | -------- | ------------------- | ------------- |
| `postcss` (≤8.5.17)            | High     | `next` internal pin | **No**        |
| `sharp` (<0.35.0)              | High     | `next` internal pin | **No**        |
| `next`                         | High     | postcss, sharp      | **No**        |
| `@storybook/nextjs-vite`       | Moderate | next (dev)          | **No**        |
| `vite-plugin-storybook-nextjs` | Moderate | next (dev)          | **No**        |

**Advisories:**

- PostCSS XSS / source map disclosure — [GHSA-qx2v-qp2m-jg93](https://github.com/advisories/GHSA-qx2v-qp2m-jg93), [GHSA-6g55-p6wh-862q](https://github.com/advisories/GHSA-6g55-p6wh-862q), [GHSA-r28c-9q8g-f849](https://github.com/advisories/GHSA-r28c-9q8g-f849)
- sharp / libvips — [GHSA-f88m-g3jw-g9cj](https://github.com/advisories/GHSA-f88m-g3jw-g9cj) (CVE-2026-33327, CVE-2026-33328, CVE-2026-35590, CVE-2026-35591)

All findings are **transitive dependencies pinned by Next.js 15.5.x** with no available patch at verification time. These do not block the existing CI pipeline (`.github/workflows/ci.yml` and `build.yml` do not gate on `npm audit`).

---

## Comparison with prior Windows audit

| Finding (Windows audit, `172fcc4f`)         | Linux RC3 result                 |
| ------------------------------------------- | -------------------------------- |
| `format:check` — 138 files fail             | **PASS** (resolved in `9f23b19`) |
| Vitest worker crash at `use-theme.test.tsx` | **PASS** — 4/4 tests green       |
| `npm run build` — `next` binary missing     | **PASS** — clean build           |
| Node 22.13.1 below engine minimum           | CI uses **22.22.1** (correct)    |
| `node_modules` corruption                   | **Not reproduced** on Linux      |

---

## CI parity matrix

| Gate            | RC3 verification | `ci.yml` PR job           | `build.yml` main job |
| --------------- | ---------------- | ------------------------- | -------------------- |
| `npm ci`        | Yes              | Yes                       | Yes                  |
| `format:check`  | Yes              | Yes                       | Yes                  |
| `typecheck`     | Via `verify`     | Yes                       | Yes                  |
| `lint`          | Via `verify`     | Yes                       | Yes                  |
| `test:run`      | Yes              | No (uses `test:coverage`) | No                   |
| `test:coverage` | Yes              | Yes                       | Yes                  |
| `build`         | Yes              | Yes                       | Yes                  |
| `npm audit`     | Yes              | No                        | No                   |
| Playwright E2E  | No               | Yes (separate job)        | No                   |

---

## Artifacts and reproduction

Re-run verification on Linux:

```bash
gh workflow run "RC3 Release Verification" --repo Raja-code-cloud/tool --ref main
gh run watch --repo Raja-code-cloud/tool
gh run download <run-id> --repo Raja-code-cloud/tool --dir rc3-verification
```

Local Windows results are **non-authoritative**. See [LOCAL_DEVELOPMENT.md](./LOCAL_DEVELOPMENT.md).

---

## Related documents

| Document                                                                                 | Purpose                             |
| ---------------------------------------------------------------------------------------- | ----------------------------------- |
| [GO_NO_GO.md](./GO_NO_GO.md)                                                             | Release decision                    |
| [LOCAL_DEVELOPMENT.md](./LOCAL_DEVELOPMENT.md)                                           | Windows-local issues (non-blocking) |
| [docs/frontend/release/RC_RELEASE_AUDIT.md](./docs/frontend/release/RC_RELEASE_AUDIT.md) | Prior audit (superseded for gates)  |
| [docs/release/RELEASE_SIGNOFF.md](./docs/release/RELEASE_SIGNOFF.md)                     | RC1 sign-off baseline               |

---

_Verification performed on Ubuntu GitHub Runner with Node 22.22.1. No application source was modified during this verification._

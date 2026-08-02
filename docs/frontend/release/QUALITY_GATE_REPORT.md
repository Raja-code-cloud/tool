# Quality Gate Report — Cloud Content Hub Frontend RC Audit

**Audit date:** 2026-08-03  
**Commit:** `172fcc4f87a4bf0853c9e34f0585978a4a28f4a6`  
**Branch:** `main`  
**Audit host:** Windows 10, Node v22.13.1, npm 10.9.2

---

## Summary

| Gate         | Status      | CI blocker?      |
| ------------ | ----------- | ---------------- |
| typecheck    | **PASS**    | Yes — would pass |
| lint         | **PASS**    | Yes — would pass |
| format       | **NOT RUN** | N/A              |
| format:check | **FAIL**    | **Yes**          |
| test         | **FAIL**    | **Yes**          |
| build        | **FAIL**    | **Yes**          |

**Overall gate status: FAIL (3 of 5 executable gates failed or unverified)**

---

## 1. Typecheck

**Command:** `npm run typecheck` → `tsc --noEmit`

| Field              | Value    |
| ------------------ | -------- |
| **Result**         | **PASS** |
| **Exit code**      | 0        |
| **Execution time** | 46.55s   |
| **Warnings**       | 0        |
| **Errors**         | 0        |

**Notes:** Strict TypeScript options enabled (`strict`, `exactOptionalPropertyTypes`, `noUncheckedIndexedAccess`, unused symbol checks).

---

## 2. Lint

**Command:** `npm run lint` → `next lint`

| Field              | Value           |
| ------------------ | --------------- |
| **Result**         | **PASS**        |
| **Exit code**      | 0               |
| **Execution time** | 36.15s          |
| **Warnings**       | 1 informational |
| **Errors**         | 0               |

**Warnings:**

```
`next lint` is deprecated and will be removed in Next.js 16.
For existing projects, migrate to the ESLint CLI:
npx @next/codemod@canary next-lint-to-eslint-cli .
```

**Policy:** `lint:eslint` script enforces `--max-warnings=0`. Primary CI path uses `next lint`.

---

## 3. Format

**Command:** `npm run format` → `prettier --write .`

| Field      | Value                                                                  |
| ---------- | ---------------------------------------------------------------------- |
| **Result** | **NOT EXECUTED**                                                       |
| **Reason** | Audit policy prohibits mutating 138 files identified by `format:check` |

**Recommendation:** Run on a dedicated formatting branch before release. Expected to touch frontend source, docs, and ancillary workspace files.

---

## 4. Format Check

**Command:** `npm run format:check` → `prettier --check .`

| Field              | Value           |
| ------------------ | --------------- |
| **Result**         | **FAIL**        |
| **Exit code**      | 1               |
| **Execution time** | 154.88s         |
| **Warnings**       | 138 files       |
| **Errors**         | 1 summary error |

**Sample affected frontend paths:**

- `app/(dashboard)/calendar/page.tsx`
- `app/(dashboard)/layout.tsx`
- `app/(dashboard)/settings/**`
- `components/buttons/**`, `components/charts/**`, `components/dialogs/**`
- `components/layout/**`, `components/navigation/**`, `components/tables/**`
- `components/ui/**`, `constants/navigation.ts`
- `hooks/**`, `lib/motion.ts`, `styles/globals.css`
- `tests/integration/**`, `tests/e2e/**`

**Also affected (non-frontend):** `backend/**`, `cloud-content-hub-prompts/**`, extensive `docs/**` markdown.

**Remediation:** `npm run format` then commit. Consider scoping Prettier to frontend paths if monorepo formatting is intentionally deferred.

---

## 5. Test

**Command:** `npm run test:run` → `vitest run`

| Field              | Value             |
| ------------------ | ----------------- |
| **Result**         | **FAIL**          |
| **Exit code**      | 1                 |
| **Execution time** | 367.16s (aborted) |
| **Warnings**       | 0                 |
| **Errors**         | 1 fatal           |

**Error output:**

```
❯ tests/unit/hooks/use-theme.test.tsx (0 test)
Error: Worker exited unexpectedly
    at Worker.emitUnexpectedExit (vitest/dist/chunks/cli-api...)
Node.js v22.13.1
```

**Retry attempts:** Subsequent runs failed because `node_modules/.bin` symlinks were missing after dependency tooling corrupted the install tree.

**Test inventory (static):**

| Suite                              | Files |
| ---------------------------------- | ----- |
| Unit — components                  | 12    |
| Unit — hooks                       | 4     |
| Unit — lib                         | 14    |
| Unit — security                    | 1     |
| Unit — app                         | 1     |
| Integration workflows              | 9     |
| E2E (Playwright, separate command) | 5     |

**CI expectation:** `npm run test:coverage` on Ubuntu Node 22.22.1 with coverage thresholds (lines 70%, statements 70%, functions 62%, branches 54%).

**Flaky / unstable:**

- `tests/unit/hooks/use-theme.test.tsx` — worker crash observed
- Full suite slow on Windows (KI-041, ~7 min historical)

---

## 6. Build

**Command:** `npm run build` → `next build`

| Field              | Value    |
| ------------------ | -------- |
| **Result**         | **FAIL** |
| **Exit code**      | 1        |
| **Execution time** | 13.14s   |
| **Warnings**       | 0        |
| **Errors**         | 1        |

**Error:**

```
'next' is not recognized as an internal or external command
```

**Root cause:** Corrupted/incomplete `node_modules` after failed reinstall (`ENOTEMPTY`, npm cache ENOENT). Not an application compile error.

**Last verified build (2026-08-02):** Pass — 13 static routes, shared JS 103 kB. See [BUILD_REPORT.md](./BUILD_REPORT.md).

---

## CI Pipeline Mapping

From `.github/workflows/ci.yml`:

```
1. npm run typecheck        → PASS (audit)
2. npm run format:check     → FAIL (audit)
3. npm run lint             → PASS (audit)
4. npm run test:coverage    → FAIL / unverified (audit)
5. npm run build            → FAIL / unverified (audit)
```

Parallel job: `npm run test:e2e` (Playwright) — not executed in this audit.

---

## Recommendations

| Priority | Action                                                              |
| -------- | ------------------------------------------------------------------- |
| P0       | Fix Prettier drift; unblock CI step 2                               |
| P0       | Restore clean `npm ci` on Node 22.22.1; verify test + build         |
| P1       | Investigate Vitest worker crash on Windows (`use-theme.test.tsx`)   |
| P1       | Migrate from deprecated `next lint` to ESLint CLI before Next.js 16 |
| P2       | Split Prettier scope if backend/docs formatting is out of RC scope  |

---

_Generated by Release Audit Engineer — no source modifications applied._

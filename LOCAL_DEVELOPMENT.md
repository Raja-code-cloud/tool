# Local Development Notes — Windows Environment

**Last updated:** 2026-08-03  
**Purpose:** Document Windows-specific development issues that **do not reproduce on production CI** (Ubuntu GitHub Runner, Node 22.22.1).

**Release source of truth:** Linux CI only. See [FINAL_RELEASE_VERIFICATION.md](./FINAL_RELEASE_VERIFICATION.md) and [GO_NO_GO.md](./GO_NO_GO.md).

---

## Summary

| Issue | Windows | Linux CI | Release blocker? |
| ----- | ------- | -------- | ---------------- |
| Node version below engine minimum | Yes (22.13.1) | No (22.22.1) | **No** |
| Vitest worker crash (`use-theme.test.tsx`) | Observed | Not reproduced | **No** |
| `node_modules` corruption after failed install | Observed | Not reproduced | **No** |
| Slow full Vitest suite (~7+ min) | Yes | ~47s | **No** |
| Prettier drift (138 files) | Was failing | Fixed at `9f23b19` | **No** (resolved) |
| npm package extraction errors | Possible | Not observed | **No** unless reproduced on CI |
| No WSL / Docker on audit host | Yes | N/A | **No** |

---

## Required toolchain

| Tool | Required | Typical Windows audit host | Action |
| ---- | -------- | -------------------------- | ------ |
| Node.js | `>=22.22.1` | v22.13.1 | Install 22.22.1 via [nvm-windows](https://github.com/coreybutler/nvm-windows) or official installer |
| npm | Bundled with Node | 10.9.x | Use npm bundled with Node 22.22.1 |
| Engine file | `.nvmrc` → `22.22.1` | — | Run `nvm use` or `fnm use` after installing |

```powershell
node --version   # Must report v22.22.1 or higher
npm ci
```

Using a Node version below the engine minimum produces **non-authoritative** test and build results.

---

## Known Windows issues

### 1. Vitest worker crash (KI-070)

**Symptom:** `vitest run` aborts with `Worker exited unexpectedly`, often at `tests/unit/hooks/use-theme.test.tsx`.

**Environment:** Windows 10, Node 22.13.1.

**Linux CI:** 4/4 tests pass in ~53ms (run #30764784803).

**Workaround:**

- Treat Linux CI as the test gate of record.
- If local verification is needed, run tests in WSL2 Ubuntu or trigger CI:
  ```powershell
  gh workflow run "RC3 Release Verification" --repo Raja-code-cloud/tool --ref main
  ```
- Vitest is configured with `pool: "threads"`, `maxWorkers: 1`, `fileParallelism: false` in `vitest.config.ts` to reduce Windows instability.

### 2. Slow test suite (KI-041)

**Symptom:** Full `npm run test:run` can take **7+ minutes** on Windows vs **~42–47 seconds** on Linux CI.

**Impact:** Local developer friction only. Pre-push hooks that run `npm run verify` are slow.

**Workaround:**

- Run targeted tests during development: `npx vitest run tests/unit/hooks/use-theme.test.tsx`
- Rely on CI for full-suite timing and stability.

### 3. `node_modules` corruption (KI-071)

**Symptom:** Interrupted or failed `npm ci` / `npm install` leaves incomplete `node_modules`; CLI binaries (e.g. `next`) missing; subsequent commands fail with "not recognized" errors.

**Workaround:**

```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json   # only if lockfile is suspect; normally keep it
npm cache clean --force
npm ci
```

**Prevention:** Always use `npm ci` (not `npm install`) for clean installs. Do not interrupt installs.

### 4. npm package extraction failures

**Symptom:** Windows antivirus, long paths, or disk locking can cause tarball extraction errors during `npm ci`.

**Classification:** **Not a release blocker** unless the same failure reproduces on Ubuntu CI.

**Workaround:**

- Exclude project directory from real-time antivirus scanning during installs.
- Enable Windows long path support.
- Retry `npm ci` after clearing `node_modules`.
- If extraction fails persistently, verify on Linux CI before treating as a product defect.

### 5. Commit and push hooks

**Symptom:** Husky pre-commit runs lint-staged; pre-push may run `npm run verify` (full format + typecheck + lint + test).

**Impact:** Slow on Windows; commit-msg requires [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat: add feature
fix: resolve bug
ci: add RC3 verification workflow
```

Invalid commit messages are rejected by commitlint.

### 6. No local Linux parity (audit host)

The verification audit host had **no WSL distribution** and **no Docker**. Local Linux parity requires one of:

- WSL2 + Ubuntu (`wsl --install Ubuntu`)
- Docker Desktop with a Node 22.22.1 container
- GitHub Actions (`gh workflow run`) — **recommended for release verification**

---

## Recommended Windows developer workflow

1. Install Node **22.22.1** (match `.nvmrc` and CI).
2. Clone and install:
   ```powershell
   git clone https://github.com/Raja-code-cloud/tool.git
   cd tool
   npm ci
   ```
3. Day-to-day development:
   ```powershell
   npm run dev          # local server
   npm run typecheck    # fast feedback
   npx vitest run path  # targeted tests
   ```
4. Before pushing, prefer CI over local full verify on Windows:
   ```powershell
   gh workflow run "Main Branch Build" --repo Raja-code-cloud/tool --ref HEAD
   ```
5. For release verification, always use the RC3 workflow on Linux (see FINAL_RELEASE_VERIFICATION.md).

---

## What NOT to do

- Do **not** use Windows-local `npm run verify` failure (especially worker crashes) as a release blocker.
- Do **not** classify Windows package extraction problems as release blockers unless reproduced on Ubuntu CI.
- Do **not** report Node 22.13.x results as RC3 verification — engine minimum is 22.22.1.
- Do **not** skip `npm ci` in favor of `npm install` for reproducible setups.

---

## CI reference commands (authoritative)

These commands were executed on Ubuntu GitHub Runner and define release readiness:

```bash
npm ci
npm run verify
npm run build
npm run test
npm run format:check
npm audit
```

Results: [FINAL_RELEASE_VERIFICATION.md](./FINAL_RELEASE_VERIFICATION.md)

---

## Related issues

| ID | Document | Topic |
| -- | -------- | ----- |
| KI-041 | `docs/frontend/release/KNOWN_ISSUES.md` | Slow Vitest on Windows |
| KI-070 | `docs/frontend/release/KNOWN_ISSUES.md` | Worker crash on Windows |
| KI-071 | `docs/frontend/release/KNOWN_ISSUES.md` | node_modules corruption |
| KL-032 | `docs/release/KNOWN_LIMITATIONS.md` | Windows test slowness accepted |

---

*Windows issues documented here are for developer awareness only. They do not override Linux CI release decisions.*

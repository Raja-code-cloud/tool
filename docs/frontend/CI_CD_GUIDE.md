# Frontend CI/CD Guide

## Overview

The frontend uses GitHub Actions with npm, Node.js **22.22.1**, and the committed
`package-lock.json`. CI reuses the repository's `typecheck`, `format:check`, `lint`,
`test:coverage`, `test:e2e`, and `build` scripts.

## Workflow map

- Pull requests to `main`: `.github/workflows/ci.yml`
- Pushes to `main`: `.github/workflows/build.yml`
- Versioned releases: `.github/workflows/release.yml`
- Dependency updates: `.github/dependabot.yml`

## Quality gates

Pull requests must pass:

| Job        | Checks                                                                 |
| ---------- | ---------------------------------------------------------------------- |
| Validate   | TypeScript, Prettier, ESLint, Vitest with coverage gate, production build |
| E2E        | Playwright (Chromium) against the Next.js dev server                   |
| Dependency | GitHub dependency review on changed packages                           |

Main branch and release workflows enforce TypeScript, formatting, ESLint, coverage, and build. Pull request E2E runs in a dedicated parallel job to keep browser startup isolated from the compile/test job.

A non-zero command exit code fails its job.

Configure branch protection on `main` to require:

- `Dependency review`
- `Type check, lint, test, and build`
- `Playwright end-to-end tests`

For the main branch, monitor:

- `Type check, lint, and test` (includes coverage gate)
- `Production build`

See [COVERAGE_STRATEGY.md](./COVERAGE_STRATEGY.md) for threshold rationale and staged rollout.

## Playwright in CI

Playwright runs in `.github/workflows/ci.yml` as the `e2e` job:

1. `npm ci`
2. `npx playwright install --with-deps chromium`
3. `npm run test:e2e` with `CI=true`

`playwright.config.ts` starts `npm run dev`, sets one worker, and enables two retries in CI. Failed runs upload `playwright-report/` and `test-results/` artifacts.

E2E is appropriate for RC3 because:

- Five spec files cover routes, accessibility, responsive layout, and user journeys
- Config already defines CI-safe server lifecycle and retry behavior
- Tests complement Vitest (browser rendering, navigation, axe scans)

Main-branch `build.yml` does not run E2E to limit push latency; PR validation is the merge gate.

## Caching

`actions/setup-node` caches npm's package cache. `actions/cache` separately
caches `node_modules` using the operating system, Node version, and lockfile
hash, and caches `.next/cache` using dependency and source hashes. A lockfile
change invalidates dependency caches.

## Environments and deployment handoff

- Development runs locally with `npm run dev`.
- Pull requests produce validation results and do not deploy.
- `main` produces a 14-day `frontend-build-<commit>` artifact suitable for a
  staging deployment job or deployment platform.
- A release produces a 90-day versioned archive and attaches it to the GitHub
  release for production deployment.

No hosting provider credentials or deployment commands are committed. Add
provider-specific staging and production jobs after selecting the deployment
target. Use GitHub Environments for `staging` and `production`, keep secrets in
environment secrets, and require approval for production.

## Security controls

Workflows default to read-only repository permissions. Only the release job can
write repository contents so it can create a tag and GitHub release. Dependabot
maintains npm and GitHub Actions dependencies.

Enable these repository settings in GitHub:

1. Secret scanning and push protection.
2. Dependabot alerts and security updates.
3. Branch protection with required reviews and status checks.
4. Actions restricted to trusted actions, with SHA pinning if organizational
   policy requires immutable references.

## Local parity

Run the same checks before opening a pull request:

```sh
npm ci
npm run verify          # format, typecheck, lint, unit tests (fast)
npm run test:coverage   # coverage gate (matches CI)
npm run test:e2e        # browser tests (matches CI)
npm run build
```

## Tooling references

- Coverage thresholds: [COVERAGE_STRATEGY.md](./COVERAGE_STRATEGY.md)
- ESLint migration: [ESLINT_MIGRATION.md](./ESLINT_MIGRATION.md)
- Build steps: [BUILD_PIPELINE.md](./BUILD_PIPELINE.md)

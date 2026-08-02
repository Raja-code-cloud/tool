# Frontend Build Pipeline

## Runtime and installation

All workflows use Ubuntu runners, Node.js 22.22.1, npm, and
`package-lock.json`. Cache misses install dependencies with:

```sh
npm ci --no-audit --no-fund
```

The lockfile remains the source of truth; CI never updates dependencies.

## Pull request pipeline

`ci.yml` runs for pull requests targeting `main`:

1. Review dependency changes.
2. Restore npm, `node_modules`, and Next.js caches.
3. Install dependencies on a dependency-cache miss.
4. Run `npm run typecheck`.
5. Run `npm run format:check`.
6. Run `npm run lint`.
7. Run `npm run test:coverage` (Vitest with RC3 coverage gate; see [COVERAGE_STRATEGY.md](./COVERAGE_STRATEGY.md)).
8. Run `npm run build`.

A parallel **Playwright end-to-end** job runs `npm run test:e2e` with Chromium.
See [CI_CD_GUIDE.md](./CI_CD_GUIDE.md) for artifact retention and branch protection requirements.

New commits cancel obsolete runs for the same pull request.

## Main branch pipeline

`build.yml` runs after pushes to `main` and supports manual dispatch:

1. The quality job installs dependencies and runs `format:check`, type checking, linting, and
   unit tests with the coverage gate (`npm run test:coverage`).
2. The production-build job starts only after quality succeeds.
3. The build job runs `npm run build`.
4. GitHub stores `.next`, package metadata, and Next.js configuration
   as `frontend-build-<commit>` for 14 days.

The artifact is a deployment handoff, not a standalone runtime bundle. A target
platform may install production dependencies or consume the Next.js build
according to that platform's deployment adapter.

## Failure behavior

GitHub Actions stops each sequential job at the first failed command. TypeScript
errors, ESLint errors, test failures, missing build output, and Next.js build
failures therefore fail the workflow.

## Cache behavior

- npm cache: managed by `actions/setup-node`, keyed from `package-lock.json`.
- `node_modules`: keyed by runner OS, Node version, and lockfile hash.
- `.next/cache`: keyed by lockfile and JavaScript/TypeScript source hashes, with
  a dependency-level restore key.

Delete the relevant Actions cache from repository settings if a corrupted cache
is suspected. Do not weaken `npm ci` lockfile guarantees to work around cache
failures.

## Artifact contents

Main branch artifacts contain:

- `.next/`
- `package.json`
- `package-lock.json`
- `next.config.ts`

Build caches are included inside `.next`; downstream deployment tooling should
ignore `.next/cache` when it does not need incremental build state.

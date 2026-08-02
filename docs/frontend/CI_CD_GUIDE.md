# Frontend CI/CD Guide

## Overview

The frontend uses GitHub Actions with npm, Node.js 22.22.1, and the committed
`package-lock.json`. CI reuses the repository's `typecheck`, `lint`, `test:run`,
and `build` scripts.

## Workflow map

- Pull requests to `main`: `.github/workflows/ci.yml`
- Pushes to `main`: `.github/workflows/build.yml`
- Versioned releases: `.github/workflows/release.yml`
- Dependency updates: `.github/dependabot.yml`

## Quality gates

Pull requests and releases must pass TypeScript, ESLint, Vitest unit/integration
tests, and a production Next.js build. A non-zero command exit code fails its job.
The PR workflow also reviews newly introduced dependency vulnerabilities.

Configure branch protection on `main` to require:

- `Dependency review`
- `Type check, lint, test, and build`

For the main branch, monitor:

- `Type check, lint, and test`
- `Production build`

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
npm run typecheck
npm run lint
npm run test:run
npm run build
```

## Test scope

Vitest unit and integration tests are enforced with `npm run test:run`.
Playwright end-to-end tests are configured but are not part of these requested
core pipelines; add a dedicated browser-test job when runner time and browser
artifact retention policies are defined.

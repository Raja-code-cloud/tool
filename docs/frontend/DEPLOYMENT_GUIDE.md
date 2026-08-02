# Deployment guide

## Prerequisites

- Node.js 22.22.1 or newer
- npm and the committed lockfile
- A clean install environment capable of running Next.js 15

## Production build

```sh
npm ci
npm run typecheck
npm run build
npm run start
```

The application uses the standard Next.js server build; no hosting provider is declared here. Choose a runtime that supports the generated Next server and configure its port/process supervision according to that platform.

## CI and release automation

Three GitHub Actions workflows are present:

- `ci.yml` validates pull requests to `main` with dependency review, Node 22.22.1,
  formatting, type-checking, linting, tests, and a production build; it caches
  dependencies and `.next/cache`.
- `build.yml` runs on `main` pushes or manual dispatch. It performs quality/build jobs and retains `.next`, `public`, package manifests, and `next.config.ts` as a 14-day artifact.
- `release.yml` is manually dispatched with a semantic version/prerelease flag. It validates `main`, applies the version only in-run, builds, packages the same runtime inputs into a tarball, retains it for 90 days, tags the captured commit, and creates a GitHub Release.

Both test steps use `npm run test --if-present`; no test script currently exists. These workflows build and publish artifacts but name no hosting target.

## Artifact safety

The release tarball includes the full `.next` tree and is attached to a GitHub Release. On a public repository that artifact is public and may include server bundles, source maps, manifests, and embedded build-time values; review `.next` contents before release. It is also not a declared `output: "standalone"` bundle, so do not assume the tarball is self-contained without installed production dependencies. Never add `.env*`, local storage captures, or unrelated repository files.

## Verification

Smoke-test every documented route, direct URL navigation, root redirect, dark/light switching, responsive shell, and client-only upload draft behavior. No frontend environment variables or backend connectivity are currently required.

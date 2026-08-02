# Deployment guide

## Prerequisites

- Node.js 22.22.1 or newer
- npm and the committed lockfile
- A clean install environment capable of running Next.js 15

## Production build

```sh
npm ci
npm run verify
npm run build
npm run start
```

The application uses the standard Next.js server build; no hosting provider is declared here. Choose a runtime that supports the generated Next server and configure its port/process supervision according to that platform.

## Environment variables

Set at deploy time (see `.env.example`):

| Variable                   | Staging example | Production example | Required               |
| -------------------------- | --------------- | ------------------ | ---------------------- |
| `NEXT_PUBLIC_APP_ENV`      | `staging`       | `production`       | Recommended            |
| `NEXT_PUBLIC_API_BASE_URL` | API staging URL | API production URL | No until backend wired |

Never embed secrets in `NEXT_PUBLIC_*` variables — they are exposed to browsers.

## CI and release automation

Three GitHub Actions workflows validate and package the frontend:

- **`ci.yml`** — pull requests to `main`: dependency review, `format:check`, `typecheck`, `lint`, `test:run`, and `build`.
- **`build.yml`** — pushes to `main`: quality job (format, typecheck, lint, test) then production build artifact (14-day retention).
- **`release.yml`** — manual dispatch: validates `main`, builds, packages tarball (90-day retention), tags commit, creates GitHub Release.

Workflows use Node 22.22.1 and `npm ci`. Playwright E2E and Storybook builds are **not** part of CI today.

No hosting-provider deploy job is committed; add provider-specific staging and production jobs after selecting a deployment target.

## Artifact safety

The release tarball includes the full `.next` tree and is attached to a GitHub Release. On a public repository that artifact is public and may include server bundles, source maps, manifests, and embedded build-time values; review `.next` contents before release. It is not a declared `output: "standalone"` bundle, so do not assume the tarball is self-contained without installed production dependencies. Never add `.env*`, local storage captures, or unrelated repository files.

## Verification

Smoke-test every documented route, direct URL navigation, root redirect, dark/light switching, responsive shell, and client-only upload draft behavior. With mock repositories, no backend connectivity is required unless `NEXT_PUBLIC_API_BASE_URL` is configured.

## Related documentation

- [CI/CD guide](./CI_CD_GUIDE.md)
- [Build pipeline](./BUILD_PIPELINE.md)
- [Release process](./RELEASE_PROCESS.md)
- Root `.env.example`

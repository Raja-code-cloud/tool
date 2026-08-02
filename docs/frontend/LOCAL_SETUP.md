# Local setup

## Prerequisites

- Node.js 22.22.1 or newer
- npm (the committed `package-lock.json` is the dependency source of truth)
- Git
- VS Code with the workspace's recommended extensions, if using VS Code

## Install and run

```sh
git clone <repository-url>
cd <repository-directory>
npm ci
npm run dev
```

Open <http://localhost:3000>. Use `npm install` only when intentionally changing
dependencies; use `npm ci` for a clean, reproducible install.

## Validate the environment

```sh
npm run verify
npm run build
```

`npm run verify` checks formatting, TypeScript, ESLint, and any configured tests.
The production build is intentionally separate because it is slower.

## Environment variables

Copy `.env.example` to `.env.local` when the project provides one. Never commit
secrets or any `.env*` file other than `.env.example`.

## Common fixes

- Wrong Node version: install a supported Node release meeting `package.json#engines`.
- Dependency drift: remove `node_modules`, then run `npm ci`.
- Stale Next.js output: run `npm run clean`, reinstall if needed, and retry.
- Editor formatting differs from CI: use the workspace recommendations and run
  `npm run format`.

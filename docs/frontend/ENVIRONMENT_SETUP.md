# Environment setup

## Requirements

- Windows, macOS, or Linux
- Node.js `>=22.22.1` (matches `package.json#engines` and CI)
- npm

## Install and run

```sh
node --version
npm ci
npm run dev
```

Use `npm install` when intentionally updating dependencies; commit the resulting lockfile changes. `package.json` uses semver ranges while `package-lock.json` records resolved versions, so CI and reproducible local setup should use `npm ci`.

## Configuration

Copy `.env.example` to `.env.local` and adjust values as needed:

| Variable | Required | Default | Purpose |
| -------- | -------- | ------- | ------- |
| `NEXT_PUBLIC_APP_ENV` | No | `development` | Logical environment exposed to the browser |
| `NEXT_PUBLIC_API_BASE_URL` | No | unset | Future HTTP API origin; unset keeps mock repositories |

Variables are validated in `lib/config/env.ts`. Do not copy backend secrets into frontend documentation or expose credentials with `NEXT_PUBLIC_` names.

## Useful commands

```sh
npm run dev
npm run typecheck
npm run lint
npm run test:run
npm run verify
npm run build
npm run start
npm run storybook
```

`npm run verify` runs format check, TypeScript, ESLint, and Vitest — the same core gates as CI (excluding production build).

## Troubleshooting

Delete generated output with `npm run clean` when diagnosing stale builds; reinstall with `npm ci` when the lockfile changes. Browser-only theme and upload-draft behavior requires local storage. No backend service or credentials are required while mock repositories are active.

## Related documentation

- [Testing guide](./TESTING_GUIDE.md)
- [Developer guide](./DEVELOPER_GUIDE.md)
- Root `.env.example`

# Environment setup

## Requirements

- Windows, macOS, or Linux
- Node.js `>=22.22.1`
- npm

## Install and run

```sh
node --version
npm ci
npm run dev
```

Use `npm install` when intentionally updating dependencies; commit the resulting lockfile changes. `package.json` uses semver ranges while `package-lock.json` records resolved versions, so CI and reproducible local setup should use `npm ci`.

## Configuration

The frontend currently consumes no environment variables, and there is no root `.env.example`. Do not copy backend variables into frontend documentation or expose secrets with `NEXT_PUBLIC_` names. If frontend configuration is added later, document its owner, validation, build/runtime scope, and safe example value at the same time.

## Useful commands

```sh
npm run dev
npm run typecheck
npm run build
npm run start
```

`npm run lint` and `npm run verify` are declared; verify the lint command works with the installed Next.js release. There is no test command or test suite at present.

## Troubleshooting

Delete generated output only when diagnosing stale builds; reinstall with `npm ci` when the lockfile changes. Browser-only theme and upload-draft behavior requires local storage. No backend service, credentials, auth provider, or API base URL is needed for the current mock-backed frontend.

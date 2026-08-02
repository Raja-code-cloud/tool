# Frontend tooling guide

## Toolchain

- npm and `package-lock.json`: reproducible dependency installation
- ESLint: Next.js, React, and TypeScript code-quality checks
- Prettier: source, configuration, and documentation formatting
- Tailwind Prettier plugin: canonical utility-class ordering
- Import-sort Prettier plugin: deterministic import groups
- Husky: repository-managed Git hooks
- lint-staged: fast checks limited to staged files
- commitlint: Conventional Commit validation
- TypeScript: strict static checking
- Storybook: isolated component development using the existing configuration

## Command reference

- `npm run dev`: run Next.js locally
- `npm run build`: create a production build
- `npm run start`: serve a production build
- `npm run lint` / `lint:fix`: check or fix ESLint issues
- `npm run typecheck`: run TypeScript without emitting files
- `npm run format` / `format:check`: write or verify Prettier formatting
- `npm run test:run` / `test:coverage`: run Vitest; coverage enforces RC3 thresholds in CI
- `npm run test:e2e`: run Playwright browser tests (also enforced in PR CI)
- `npm run verify`: run the local quality gate (format, typecheck, lint, unit tests)
- `npm run storybook` / `build-storybook`: run or build Storybook
- `npm run lint:eslint`: direct ESLint CLI (migration path; see ESLINT_MIGRATION.md)
- `npm run clean`: remove generated frontend output

## VS Code

Open the repository folder, install the recommended extensions, and use:

- Run and Debug for server, browser, or full-stack Next.js debugging.
- **Tasks: Run Task** for development, verification, build, and Storybook.
- the workspace TypeScript version from `node_modules`.

Workspace settings are committed so formatting, ESLint fixes, import behavior,
line endings, and rulers are consistent across contributors.

## Updating tooling

Change dependencies with npm so both `package.json` and `package-lock.json` are
updated. Run `npm run verify` and `npm run build`, then test the affected hook or
editor task. Keep configuration in the repository; avoid relying on global tools.

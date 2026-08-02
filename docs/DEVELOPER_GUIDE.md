# Developer guide — Cloud Content Hub AI Frontend

This guide is the entry point for frontend and backend engineers working on the Cloud Content Hub AI workspace UI. Detailed frontend topics live under [docs/frontend/](./frontend/).

## Architecture

The application uses the **Next.js 15 App Router** with **React 19**. Route pages compose feature views; route-local hooks coordinate view state and call services; services depend on mock repositories today. Shared components stay domain-neutral.

**Data flow (current):**

```text
constants/mock data → repositories → services → client feature hooks → feature views
```

**Folder layout:**

| Path | Purpose |
| ---- | ------- |
| `app/` | Layouts, route pages, metadata, and route boundaries |
| `app/(dashboard)/*/_components/` | Route-local feature views, hooks, and components |
| `components/` | Exported shared UI by category (`layout`, `navigation`, `forms`, etc.) |
| `hooks/` | Shared sidebar, toast, pagination, and theme-facing state |
| `constants/` | Stable values and mock feature data |
| `lib/services/`, `lib/adapters/` | Use-case and mock data-source boundaries |
| `lib/domain/` | Repository contracts and domain types |
| `lib/config/env.ts` | Validated frontend environment variables |
| `styles/` | Global Tailwind theme and utilities |
| `tests/` | Vitest unit/integration tests, Playwright E2E, MSW mocks |

The `(dashboard)` route group is organizational and does not appear in URLs. Feature UI is colocated under each route's `_components/` directory — not under a top-level `features/` folder.

See [Folder structure](./frontend/FOLDER_STRUCTURE.md) for route details.

## Environment variables

Copy `.env.example` to `.env.local` for local development:

| Variable | Required | Default | Purpose |
| -------- | -------- | ------- | ------- |
| `NEXT_PUBLIC_APP_ENV` | No | `development` | Logical environment: `development`, `staging`, or `production` |
| `NEXT_PUBLIC_API_BASE_URL` | No | unset | Base URL for future HTTP repository adapters |

When `NEXT_PUBLIC_API_BASE_URL` is unset, all data comes from in-memory mock repositories. Never put secrets in `NEXT_PUBLIC_*` variables.

Validation is centralized in `lib/config/env.ts`. Import `env` instead of reading `process.env` directly.

## Shared code conventions

- Import from category entry points: `@/components/layout`, `@/components/ui`, etc.
- Use `cn` for class composition and formatting utilities for locale-aware output.
- TypeScript is strict (exact optional properties, unchecked indexed access, unused checks).
- Keep imports at module scope; use the `@/*` root alias.
- Add `"use client"` only at the smallest browser-dependent boundary.
- Use exhaustive handling for unions/enums.

## Testing

The frontend has a full test stack:

| Tool | Purpose | Command |
| ---- | ------- | ------- |
| **Vitest** | Unit and integration tests | `npm run test:run` |
| **Playwright** | Browser E2E tests | `npm run test:e2e` |
| **MSW** | HTTP mocking in Vitest | configured in `tests/mocks/` |
| **vitest-axe** | Component accessibility checks | used via `@/tests/utils` |
| **Storybook 10** | Isolated component development | `npm run storybook` |

**Test locations:**

- `tests/unit/` — utilities, hooks, components
- `tests/integration/` — feature workflows
- `tests/e2e/` — Playwright specs

CI runs Vitest on every pull request and `main` push. Playwright and Storybook are local/optional today.

See [Testing guide](./frontend/TESTING_GUIDE.md) for full detail.

## Developer workflow

```sh
npm ci
npm run dev          # local development
npm run verify       # format + typecheck + lint + test (pre-push hook)
npm run build        # production build before PR when build behavior changed
```

Git hooks (Husky):

- **pre-commit:** lint-staged (ESLint fix + Prettier on staged files)
- **pre-push:** `npm run verify`
- **commit-msg:** commitlint (Conventional Commits)

## Backend integration

Backend engineers should:

1. Set `NEXT_PUBLIC_API_BASE_URL` to the API origin (e.g., `http://localhost:8000`).
2. Implement HTTP repository adapters matching contracts in `lib/domain/`.
3. Wire adapters in `lib/adapters/` — the scaffold in `lib/services/index.ts` creates an API client when the URL is set.
4. Do not add network calls directly in React components; go through services.

Until adapters are wired, the UI operates entirely on mock data with no backend dependency.

## Validation before review

```sh
npm run verify
npm run build
```

Optional local checks:

```sh
npm run test:coverage
npm run test:e2e
npm run build-storybook
```

## Related documentation

- [Frontend overview](./frontend/FRONTEND_OVERVIEW.md)
- [Testing guide](./frontend/TESTING_GUIDE.md)
- [Environment setup](./frontend/ENVIRONMENT_SETUP.md)
- [CI/CD guide](./frontend/CI_CD_GUIDE.md)
- [Deployment guide](./frontend/DEPLOYMENT_GUIDE.md)
- [Accessibility guide](./frontend/ACCESSIBILITY_GUIDE.md)
- [Component guide](./frontend/COMPONENT_GUIDE.md)

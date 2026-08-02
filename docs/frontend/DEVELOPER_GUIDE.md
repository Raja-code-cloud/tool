# Developer guide

## Architecture

App Router pages compose feature views; route-local hooks coordinate view state and call services; services depend on mock repositories. Shared components stay domain-neutral. Root and dashboard layouts own cross-cutting providers and shell composition.

## Folders

- `app/`: layouts, route pages, metadata, and route boundaries
- `app/(dashboard)/*/_components/`: route-local feature views, hooks, and components
- `components/`: exported shared UI by category
- `hooks/`: shared sidebar, toast, and pagination state
- `constants/`: stable values and mock feature data
- `lib/services/`, `lib/adapters/`: use-case and mock data-source boundaries
- `lib/domain/`: repository contracts and domain types
- `lib/config/env.ts`: validated frontend environment variables
- `lib/`: formatting, class-name, feature, and motion utilities
- `styles/`: global Tailwind theme and utilities
- `tests/`: Vitest unit/integration, Playwright E2E, MSW mocks, and test utilities

See [Folder structure](FOLDER_STRUCTURE.md) for route details.

## Shared code

Import from category entry points such as `@/components/layout` and `@/components/ui`. Use `cn` for class composition, formatting utilities for locale-aware output, and shared motion definitions rather than duplicating values.

## Standards

- TypeScript is strict, including exact optional properties, unchecked indexed access, unused checks, and fallthrough checks.
- Keep imports at module scope and use the `@/*` root alias.
- Components and types use PascalCase; hooks use `useX`; values/functions use camelCase; constants use descriptive uppercase names.
- Prefer semantic props and native elements; forward intrinsic props where the shared contract does so.
- Add `"use client"` only at the smallest browser-dependent boundary.
- Keep network/storage concerns out of presentational components.
- Use exhaustive handling for unions/enums.

## Patterns

Compose pages from `PageContainer`, `PageHeader`, cards, and feature-local sections. Use controlled Radix primitives for complex inputs. Put reusable behavior in hooks, domain operations in services, and data-source details in repositories. Treat mock behavior as current implementation—not as an API guarantee.

## Environment

Copy `.env.example` to `.env.local`. See [Environment setup](ENVIRONMENT_SETUP.md) for install steps and variable detail.

## Testing

The project uses **Vitest** (unit + integration), **Playwright** (E2E), **MSW** (HTTP mocking), **vitest-axe** and **@axe-core/playwright** (accessibility), and **Storybook 10** (component isolation).

```sh
npm run test:run       # CI-style Vitest run
npm run test:coverage  # with coverage thresholds
npm run test:e2e       # Playwright (local; not in CI)
npm run storybook      # component development
npm run verify         # format + typecheck + lint + test:run
```

See [Testing guide](TESTING_GUIDE.md) for folder structure, mock strategy, and CI behavior.

## Validation

Run `npm run verify` before opening a pull request. Run `npm run build` when build behavior or routing changed. Pre-push hook runs `verify` automatically.

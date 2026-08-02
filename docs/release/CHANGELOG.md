# Changelog

All notable changes to the Cloud Content Hub AI frontend are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- Release documentation pack under `docs/release/` (checklists, notes, rollback plan, versioning guide)

### Fixed

- _(none — pending resolution of typecheck, lint, format, and test blockers)_

---

## [1.0.0] — TBD

First production release of the Cloud Content Hub AI frontend workspace.

### Added

#### Application shell and platform

- Next.js 15 App Router foundation with React 19 and strict TypeScript
- Dashboard route group with `WorkspaceShell`, `SidebarProvider`, and responsive navigation
- Root redirect from `/` to `/dashboard`
- Theme provider with light/dark semantic tokens and local storage persistence
- Toast notification system, skip link, loading and error UI
- Global security headers (CSP, frame options, referrer policy)
- Locale-aware formatting utilities for numbers, dates, currency, and bytes

#### Product workflows (mock-backed)

- **Dashboard** — KPI cards, recent content table, AI suggestions panel, publishing calendar agenda
- **Content Library** — grid/list toggle, filter sidebar, search, content preview panel
- **Upload Wizard** — multi-step flow (project info, master article, platform selection, review) with local draft persistence
- **AI Studio** — platform content generation, tone transforms, hashtags, CTA, suggestions drawer, version history
- **Scheduler** — calendar views (month/week/day/agenda), queue panel, quick schedule dialog, conflict alerts, notifications bar
- **Analytics** — summary cards, Recharts visualizations, filters, insights panel, top posts table
- **Social Accounts** — platform cards, connect/reconnect dialogs (simulated OAuth)
- **Settings** — workspace, AI providers, notifications, billing, and members sections
- **Calendar** — navigation entry with placeholder page

#### Component library

- Radix-based UI primitives (dialog, dropdown, select, switch, toast, etc.)
- Composed categories: layout, navigation, buttons, cards, forms, tables, charts, upload, calendar, dialogs, feedback
- Framer Motion animation variants and shared motion tokens
- react-dropzone upload components and react-day-picker calendar components

#### Data and services layer

- Mock constants, repositories, and services for all product domains
- Zod-validated environment configuration (`lib/config/env.ts`)
- HTTP API client scaffold (`lib/api/client.ts`) for future backend wiring
- MSW integration test foundation

#### Testing and quality

- Vitest unit tests (`tests/unit/`)
- Vitest integration tests with MSW (`tests/integration/`)
- Playwright E2E scaffold (`tests/e2e/`)
- ESLint with `--max-warnings=0`, Prettier, Husky pre-commit hooks, commitlint

#### Storybook

- Storybook 10 with a11y, docs, and themes addons
- 11 story modules covering component categories

#### CI/CD

- Pull request validation workflow (typecheck, format, lint, test, build, dependency review)
- Main branch build workflow with 14-day artifact retention
- Manual release workflow with semver validation, tarball packaging, and GitHub Release creation
- Dependabot for npm and GitHub Actions

#### Documentation

- Frontend documentation suite under `docs/frontend/` (20+ guides)
- Backend API and architecture documentation under `docs/backend/`
- UI/UX specification and coding standards under `docs/`

### Known issues at release

- TypeScript errors in dashboard publishing panel and upload wizard state
- ESLint unused-import warnings in scheduler and social-accounts constants
- Widespread Prettier formatting drift (272 files)
- Calendar route is a placeholder
- No production deployment automation beyond artifact packaging
- No authentication or live backend integration

---

## [0.1.0] — 2026 (development)

Initial development version recorded in `package.json`.

- Workspace shell and settings foundation
- Single git commit baseline: `d1c2f67`

[Unreleased]: https://github.com/ORG/cloud-content-hub-ai/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/ORG/cloud-content-hub-ai/releases/tag/v1.0.0
[0.1.0]: https://github.com/ORG/cloud-content-hub-ai/releases/tag/v0.1.0

# Cloud Content Hub AI — Frontend

A production-oriented Next.js 15 App Router workspace UI with React 19, Tailwind CSS v4, semantic light/dark tokens, accessible Radix primitives, and mock-backed product workflows.

## Quick start

```sh
npm ci
cp .env.example .env.local   # optional
npm run dev
```

Open `http://localhost:3000` (redirects to `/dashboard`).

## Verify

```sh
npm run verify    # format, typecheck, lint, tests
npm run build
```

## Documentation

- [Developer guide](docs/DEVELOPER_GUIDE.md) — architecture, env vars, testing, backend integration
- [Frontend docs index](docs/frontend/README.md)
- [Testing guide](docs/frontend/TESTING_GUIDE.md)
- [Release checklist](docs/release/RELEASE_CHECKLIST.md)
- [Environment template](.env.example)

## Environment variables

| Variable                   | Required | Default                   |
| -------------------------- | -------- | ------------------------- |
| `NEXT_PUBLIC_APP_ENV`      | No       | `development`             |
| `NEXT_PUBLIC_API_BASE_URL` | No       | unset (mock repositories) |

See `.env.example` for details.

## Architecture note

Feature UI is colocated under `app/(dashboard)/*/_components/`. Shared components export from `components/` by category. Data flows through mock repositories and services until `NEXT_PUBLIC_API_BASE_URL` activates HTTP adapters.

## Consumption

Import from intentional category exports:

```tsx
import { PrimaryButton } from "@/components/buttons";
import { ContentCard } from "@/components/cards";
import { PageContainer, PageHeader } from "@/components/layout";
import { SearchBar } from "@/components/navigation";
```

Interactive shell state is provider-backed:

```tsx
import { ThemeProvider, useTheme } from "@/components/theme/theme-provider";
import { SidebarProvider } from "@/hooks/use-sidebar";
import { AppToastProvider, useToast } from "@/hooks/use-toast";
```

## Public categories

- `components/ui`: accessible primitives, menus, and low-level toast parts
- `components/layout`: shell, headers, containers, stacks, and skip link
- `components/navigation`: sidebar, menu items, search, user/notification controls, breadcrumbs, tabs, pagination
- `components/buttons`: semantic button compositions and copy action
- `components/cards`: content, metric/stat, analytics, interactive, and upload cards
- `components/forms`: fields, search input, character count, and error summary
- `components/tables`: data table, sorting, toolbar, and empty state
- `components/charts`: accessible chart frame/container, legend, basic bars, data alternative, and KPI widget
- `components/upload`: dropzone, file card/queue item, and progress
- `components/calendar`: single/range calendars, date picker, and agenda
- `components/dialogs`: dialog/modal, drawer, and confirmation
- `components/feedback`: alerts, states, progress, skeletons, spinner, live region, and loading overlay
- `hooks`: `useTheme`, `useSidebar`, `useToast`, and `usePagination`
- `lib/utils/formatting`: locale-aware number, money, percent, date, and byte formatting
- `lib/motion`: shared durations, easings, and variants

## Responsive and theme conventions

Tailwind screens are `tablet` (768px), `desktop` (1024px), and `wide` (1440px). Mobile is below 768px. The server-rendered default is dark; theme changes occur after hydration and persist in local storage without changing the initial HTML.

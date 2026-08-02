# Frontend foundation

A production-oriented Next.js 15 App Router foundation with React 19, Tailwind CSS v4, semantic light/dark tokens, Inter, accessible Radix primitives, and reusable application-shell components.

## Run

```sh
npm run dev
npm run typecheck
npm run lint
npm run build
```

## Consumption

Import from the intentional category exports:

```tsx
import { PageContainer, PageHeader } from "@/components/layout";
import { PrimaryButton } from "@/components/buttons";
import { ContentCard } from "@/components/cards";
import { SearchBar } from "@/components/navigation";
```

Interactive shell state is provider-backed:

```tsx
import { SidebarProvider } from "@/hooks/use-sidebar";
import { AppToastProvider, useToast } from "@/hooks/use-toast";
import { ThemeProvider, useTheme } from "@/components/theme/theme-provider";
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

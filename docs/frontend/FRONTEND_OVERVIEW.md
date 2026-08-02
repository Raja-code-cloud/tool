# Frontend overview

The application uses the Next.js App Router. The root layout supplies Inter, metadata, `ThemeProvider`, `AppToastProvider`, and `SkipLink`. The `(dashboard)` route group adds `SidebarProvider` and `WorkspaceShell`; the group does not alter URLs.

## Runtime architecture

Route pages select feature views. Interactive views and hooks are client components; layouts and pages remain server components unless browser behavior requires otherwise. Current data flows:

`constants/mock data → repositories → services → client feature hooks → feature views`

There are no frontend API routes, Server Actions, authentication, `fetch` client, ISR/revalidation, Suspense boundaries, or remote cache. Dynamic imports inside feature views and App Router route splitting reduce initial bundles.

## Product areas

The implemented workspace includes dashboard, content library, upload, AI studio, scheduler, analytics, social accounts, and settings. Calendar is presently a placeholder.

## Shared platform

`components/` provides UI primitives and composed layout, navigation, cards, forms, tables, charts, upload, calendar, dialog, and feedback elements. Semantic CSS tokens support light and dark themes. Shared hooks own sidebar, toast, pagination, and theme-facing interaction.

## Integration boundary

Backend integration is future work. Preserve service interfaces and replace mock repositories with HTTP-backed implementations rather than introducing network calls directly into components.

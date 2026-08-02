# Routing guide

The application uses the Next.js App Router.

| URL                | Purpose                         |
| ------------------ | ------------------------------- |
| `/`                | Server redirect to `/dashboard` |
| `/dashboard`       | Workspace overview              |
| `/content-library` | Content library                 |
| `/upload`          | Upload workflow                 |
| `/ai-studio`       | AI studio                       |
| `/scheduler`       | Scheduling workflow             |
| `/calendar`        | Placeholder page                |
| `/analytics`       | Analytics                       |
| `/social-accounts` | Social account management       |
| `/settings`        | Workspace settings              |

All named pages live below `app/(dashboard)/`. The group does not appear in URLs. Its layout wraps every workspace route with `SidebarProvider` and `WorkspaceShell`; the root layout wraps the entire app with theme, toast, and skip-link support.

Navigation paths are centralized in `constants/navigation`; use those constants and Next navigation components/APIs rather than duplicating strings. Root metadata derives the product title/description from workspace constants and uses a title template.

App Router route splitting is active. Page transitions remount from the shell on pathname changes. No frontend API routes exist.

## Boundaries

The root `app/not-found.tsx` handles unmatched routes. `app/(dashboard)/loading.tsx` supplies the shared workspace loading UI, while `app/(dashboard)/error.tsx` is the workspace error boundary. Settings adds a route-specific `app/(dashboard)/settings/loading.tsx`. There is no root `app/loading.tsx` or root `app/error.tsx`, and the application does not declare manual React `Suspense` boundaries.

Add further colocated `loading.tsx`, `error.tsx`, or `not-found.tsx` files only when route-specific behavior is required. Calendar must remain described as a placeholder until a real feature replaces it.

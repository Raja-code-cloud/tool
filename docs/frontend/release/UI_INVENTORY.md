# UI Inventory — Cloud Content Hub Frontend RC Audit

**Audit date:** 2026-08-03  
**Commit:** `172fcc4f87a4bf0853c9e34f0585978a4a28f4a6`

---

## Pages

| Route              | Label           | Purpose                                                         | Status          |
| ------------------ | --------------- | --------------------------------------------------------------- | --------------- |
| `/`                | Home            | Redirect to dashboard                                           | Complete        |
| `/dashboard`       | Dashboard       | KPI overview, AI suggestions, publishing agenda, recent content | Complete        |
| `/content-library` | Content Library | Browse, filter, search, preview content assets                  | Complete        |
| `/upload`          | Upload Wizard   | 8-step guided upload with draft persistence                     | Complete        |
| `/ai-studio`       | AI Studio       | Multi-platform AI content generation workspace                  | Complete        |
| `/scheduler`       | Scheduler       | Queue, calendar views, scheduling, conflicts                    | Complete        |
| `/calendar`        | Calendar        | Editorial calendar                                              | **Placeholder** |
| `/analytics`       | Analytics       | Engagement, reach, performance reporting                        | Complete        |
| `/social-accounts` | Social Accounts | Connect and manage publishing platforms                         | Complete        |
| `/settings`        | Settings        | Workspace configuration and preferences                         | Complete        |

**Error/utility routes:** `app/not-found.tsx`, `app/(dashboard)/error.tsx`, `app/(dashboard)/loading.tsx`, `app/(dashboard)/settings/loading.tsx`

---

## Features (by Module)

### Dashboard

- Personalized greeting and workspace health
- 4 metric/stat cards with trends
- AI suggestions panel
- Publishing calendar panel (today's agenda)
- Recent content table
- Bottom modules: activity, platform health, storage

### Content Library

- Filter sidebar (status, type, platform, favorites)
- Toolbar: search, sort, grid/list toggle, refresh
- Grid view with bulk select, favorites, delete
- List view with sortable DataTable
- Preview drawer; mobile filter drawer
- Pagination and empty states

### Upload Wizard

- 8 steps: project info → poster → article → video → thumbnail → AI settings → review → finish
- Step validation, progress header, sidebar/mobile steppers
- File upload with client validation
- Draft auto-save (localStorage, 7-day TTL)
- Exit confirmation dialog

### AI Studio

- 3-panel layout: assets, editor, preview
- Per-platform generation with character limits
- AI settings, version history, suggestions drawer
- Draft save; mobile panel tabs

### Scheduler

- Analytics widget, notifications, conflict alerts
- Queue panel; calendar day/week/month/agenda views
- Details panel; quick schedule dialog
- Toolbar filters; mobile tabs

### Analytics

- Date range and platform filters
- 6 KPI summary cards
- Charts: publishing trend, engagement, reach, AI usage
- Performance tables: platform comparison, posting times, content types
- Top/worst posts; insights panel

### Social Accounts

- Overview stat cards
- Account grid with health/token badges
- Connect dialog (simulated OAuth)
- Account details drawer

### Settings

- Profile, appearance, notifications
- AI providers, storage, publishing
- Security (2FA toggle, sessions)
- API keys table; danger zone

### Calendar (Placeholder)

- `FeaturePlaceholder` / coming-soon UI

---

## Reusable Components (`components/`)

### Buttons (`components/buttons/`)

`ActionButton`, `CopyButton`, `DestructiveButton`, `IconButton`, `OutlineButton`, `PrimaryButton`, `SecondaryButton`

### Cards (`components/cards/`)

`AnalyticsCard`, `Card`, `CardHeader`, `ContentCard`, `InteractiveCard`, `MetricCard`, `StatCard`, `UploadCard`

### Charts (`components/charts/`)

`BarChart`, `ChartContainer`, `ChartDataTable`, `ChartFrame`, `ChartLegend`, `KPIWidget`

### Calendar (`components/calendar/`)

`AgendaList`, `CalendarRange`, `CalendarSingle`, `DatePicker`

### Common (`components/common/`)

`AvatarGroup`, `KeyValueList`, `Toolbar`, `VisuallyHidden`

### Dialogs (`components/dialogs/`)

`ConfirmationDialog`, `Dialog`, `DialogClose`, `DialogContent`, `DialogTrigger`, `DrawerContent`, `Modal`, `ModalContent`, `ModalTrigger`

### Feedback (`components/feedback/`)

`Alert`, `EmptyState`, `ErrorState`, `LiveRegion`, `LoadingOverlay`, `NoContent`, `NoData`, `NoResults`, `Progress`, `Skeleton`, `SkeletonCard`, `SkeletonTable`, `SkeletonText`, `Spinner`, `StatusBadge`

### Filters (`components/filters/`)

`FilterBar`, `FilterChip`, `FilterGroup`, `FilterSearch`, `FilterSelect`

### Forms (`components/forms/`)

`CharacterCount`, `FormErrorSummary`, `FormField`, `SearchBar`, `SearchField`, `SearchInput`

### Layout (`components/layout/`)

`AppHeader`, `AppShell`, `Container`, `Navbar`, `PageContainer`, `PageHeader`, `SkipLink`, `Stack`, `TopNavbar`, `WorkspaceShell`, `PageTransition`

### Navigation (`components/navigation/`)

`Breadcrumbs`, `NavItem`, `NotificationButton`, `Pagination`, `SearchBar`, `Sidebar`, `SidebarMenu`, `SidebarTrigger`, `Tabs`, `UserMenu`

### Platform (`components/platform/`)

`PLATFORM_CONFIG`, `PlatformAvatar`, `PlatformBadge`, `PlatformChip`, `PlatformDots`, `PlatformIcon`, `SUPPORTED_PLATFORM_IDS`, `getPlatformConfig`, `isPlatformId`

### Tables (`components/tables/`)

`DataTable`, `EmptyTableState`, `SortButton`, `TableToolbar`

### Theme (`components/theme/`)

`ThemeProvider`, `useTheme`, `ThemeToggle`

### UI Primitives (`components/ui/`)

`Avatar`, `Badge`, `Button`, `Checkbox`, `Input`, `Label`, `RadioGroup`, `RadioGroupItem`, `Select`, `SelectContent`, `SelectItem`, `SelectTrigger`, `SelectValue`, `Separator`, `Switch`, `Textarea`, `Toast`, `ToastProvider`, `DropdownMenu` (+ items), `badgeVariants`, `buttonVariants`

### Upload (`components/upload/`)

`FileCard`, `UploadDropzone`, `UploadProgress`, `UploadQueueItem`, `UploadZone`

### Shared (no barrel)

`SelectField` — `components/shared/select-field.tsx`

---

## Dialogs

### Design System

`Dialog`, `Modal`, `DialogContent`, `ModalContent`, `DrawerContent`, `ConfirmationDialog`

### Application Dialogs

| Dialog                | Location             | Purpose                   |
| --------------------- | -------------------- | ------------------------- |
| WizardExitDialog      | upload               | Confirm leaving wizard    |
| ConnectAccountDialog  | social-accounts      | Platform OAuth picker     |
| AccountDetailsDrawer  | social-accounts      | Account detail slide-over |
| QuickScheduleDialog   | scheduler            | Schedule new post         |
| ContentPreviewPanel   | content-library      | Content preview drawer    |
| Mobile filters drawer | content-library      | Filter sidebar on mobile  |
| Delete confirmation   | content-library      | Bulk/single delete        |
| SuggestionsDrawer     | ai-studio            | AI suggestions            |
| Revoke session        | settings/security    | Session revoke confirm    |
| Revoke API key        | settings/api-keys    | Key revocation confirm    |
| Delete workspace      | settings/danger-zone | Destructive confirm       |

---

## Forms

| Form                  | Location                       | Controls                             |
| --------------------- | ------------------------------ | ------------------------------------ |
| Profile               | settings/profile-section       | Input, Textarea, SelectField         |
| Appearance            | settings/appearance-section    | RadioGroup, Switch                   |
| Notifications         | settings/notifications-section | Checkbox matrix                      |
| AI Providers          | settings/ai-providers-section  | Connect actions                      |
| Storage               | settings/storage-section       | SelectField, Switch                  |
| Publishing            | settings/publishing-section    | Input, SelectField, Switch           |
| Security              | settings/security-section      | Switch, ConfirmationDialog           |
| Step: Project Info    | upload                         | FormField, Input, Textarea, Select   |
| Step: Master Article  | upload                         | Textarea, CharacterCount             |
| Step: AI Settings     | upload                         | Platform chips, RadioGroup, Checkbox |
| Step: Video/Thumbnail | upload                         | Checkbox skip, UploadZone            |
| Quick Schedule        | scheduler                      | FormField, Input, SelectField        |
| AI Studio editor      | ai-studio                      | Textarea per platform                |
| AI Settings panel     | ai-studio                      | RadioGroup, Checkbox                 |

---

## Charts

### Design System

`BarChart`, `ChartFrame`, `ChartLegend`, `ChartDataTable`, `KPIWidget`

### Application

| Chart                    | Route     | Library                           |
| ------------------------ | --------- | --------------------------------- |
| Publishing trend         | Analytics | Recharts LineChart                |
| Engagement by platform   | Analytics | Custom BarChart                   |
| Reach by platform        | Analytics | Recharts PieChart                 |
| AI usage trend           | Analytics | Recharts AreaChart                |
| Best posting times       | Analytics | Custom BarChart                   |
| Content type performance | Analytics | Custom BarChart                   |
| Dashboard stats          | Dashboard | MetricCard sparkline placeholders |
| Scheduler analytics      | Scheduler | Metric cards (no chart)           |

---

## Tables

### Design System

`DataTable`, `SortButton`, `TableToolbar`, `EmptyTableState`

### Application

| Table               | Route           |
| ------------------- | --------------- |
| RecentContentTable  | Dashboard       |
| ContentListView     | Content Library |
| TopPostsTable       | Analytics       |
| Platform comparison | Analytics       |
| API Keys            | Settings        |

---

## Layouts

| Layout          | File                                    | Role                                    |
| --------------- | --------------------------------------- | --------------------------------------- |
| Root            | `app/layout.tsx`                        | HTML shell, fonts, providers, skip link |
| Dashboard group | `app/(dashboard)/layout.tsx`            | SidebarProvider + WorkspaceShell        |
| AppShell        | `components/layout/layout.tsx`          | Sidebar + header + main landmark        |
| WorkspaceShell  | `components/layout/workspace-shell.tsx` | Full app chrome                         |
| PageContainer   | `components/layout/layout.tsx`          | Content wrapper                         |
| Stack           | `components/layout/layout.tsx`          | Vertical spacing                        |
| PageHeader      | `components/layout/layout.tsx`          | Title, description, actions             |
| PageTransition  | `components/layout/page-transition.tsx` | Route animation                         |
| Settings layout | settings/page.tsx                       | Nav + section stack                     |

---

## Navigation Elements

| Element                | Location                               |
| ---------------------- | -------------------------------------- |
| Sidebar                | WorkspaceShell — 9 NAV_ROUTES          |
| SidebarTrigger         | AppHeader — mobile drawer              |
| Breadcrumbs            | AppHeader — pathname-derived           |
| SearchBar              | AppHeader — placeholder (Ctrl/Cmd+K)   |
| Quick Actions dropdown | WorkspaceShell — Upload, AI, Scheduler |
| NotificationButton     | AppHeader — mock unread badge          |
| UserMenu               | AppHeader — profile, sign-out          |
| ThemeToggle            | Header area                            |
| SettingsNav            | Settings — anchor jump list            |
| Pagination             | Content Library                        |
| Tabs                   | AI Studio, Scheduler mobile            |
| Dashboard quick links  | DashboardHeader                        |
| ROUTES / NAV_ROUTES    | `constants/navigation.ts`              |

---

## Storybook Stories

11 story files under `stories/` covering buttons, cards, charts, dialogs, feedback, forms, layout, navigation, tables, theme, upload.

---

_Inventory reflects static analysis of `app/`, `components/`, and `constants/navigation.ts`._

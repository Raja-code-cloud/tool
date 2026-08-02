# Component guide

Public shared components are exported through category `index.ts` files. Feature-local components under `app/(dashboard)/*/_components/` are not shared API. “Library-ready” below means exported but not necessarily used by a current route.

## UI primitives

- `Button` — intrinsic button props plus `variant` (`primary`, `secondary`, `outline`, `ghost`, `destructive`, `icon`), `size` (`compact`, `default`, `prominent`), `asChild`, and `isLoading=false`. `buttonVariants` exposes its CVA recipe.
- `Input`, `Textarea`, `Label`, `Checkbox`, `Switch`, `RadioGroup`, `RadioGroupItem` — styled intrinsic/Radix contracts.
- `Select`, `SelectValue`, `SelectTrigger`, `SelectContent`, `SelectItem` — Radix select subparts; content defaults to `position="popper"`.
- `Badge` — intrinsic span plus semantic variant; default `neutral`. `badgeVariants` exposes its recipe.
- `Avatar` — requires `alt`; optional `src`, `fallback`, and `size="md"` (`sm|md|lg`).
- `Separator` — horizontal by default; accepts `vertical`.
- `DropdownMenu`, `DropdownMenuTrigger`, `DropdownMenuContent`, `DropdownMenuItem`, `DropdownMenuCheckboxItem`, `DropdownMenuSeparator`, `DropdownMenuLabel` — Radix menu family. Content defaults `sideOffset=6`; items support `isDestructive=false`.
- `ToastProvider`, `Toast` — low-level Radix toast parts; `Toast` requires `title` and optionally accepts `description` and `action`.

## Layout and navigation

- `Container`/`PageContainer` — width container; `size="content"` or `"reading"`.
- `Stack` — vertical stack; `gap="md"` (`sm|md|lg`).
- `PageHeader` — requires `title`; optional description, actions, breadcrumbs, and heading attributes.
- `AppShell` — optional sidebar/header plus required children and `#main-content`.
- `SkipLink` — defaults to `#main-content` and “Skip to content”.
- `AppHeader`, `TopNavbar`, `Navbar` — header aliases/compositions; accept leading, search, actions, and title.
- `WorkspaceShell` — active dashboard shell; `PageTransition` animates route changes.
- `Breadcrumbs`, `NavItem`, `Sidebar`, `SidebarMenu`, `SidebarTrigger`, `NotificationButton`, `UserMenu`, `Tabs`, `Pagination`, `SearchBar` — navigation contracts are defined by their exported prop types. These are active shell/library components; supply labels and item arrays rather than embedding domain state.

## Buttons

`PrimaryButton`, `SecondaryButton`, `OutlineButton`, `DestructiveButton`, `IconButton`, and `ActionButton` are semantic `Button` compositions. `CopyButton` accepts its exported copy contract and uses clipboard/browser feedback, so importing it makes the consuming boundary client-side; keep that boundary narrow.

## Cards and forms

- `Card` — intrinsic article/section/div (`as="div"`); `ContentCard` is its alias.
- `CardHeader` — title required; description/action optional; `headingLevel=3`.
- `MetricCard` — label/value required; optional trend, comparison, visualization. `StatCard` and `AnalyticsCard` are aliases.
- `InteractiveCard` — requires `href` and `title`; whole-card link treatment.
- `UploadCard` — dashed-border `Card`.
- `FormField` — requires `id`, `label`, and one child; injects accessibility attributes. Optional required, description, error.
- `CharacterCount` — `current` and `maximum`.
- `FormErrorSummary` — errors required; default title “Please fix the following”; renders nothing when empty.
- `SearchField`, `SearchInput`, `SearchBar` — aliases; default accessible label “Search”, plus separate wrapper/input classes.

## Tables, charts, upload, and calendar

- `DataTable<T>` — caption, columns, rows, and row-id function required; `density="default"`, customizable empty state. `SortButton` defaults to no direction; `TableToolbar` label defaults to “Table controls”; `EmptyTableState` title defaults to “No results”.
- `ChartContainer`, `ChartFrame`, `ChartLegend`, `BarChart`, `ChartDataTable`, `KPIWidget` — library-ready accessible chart compositions. Pair visual charts with labels/data alternatives; use exported `ChartDatum` and legend contracts.
- `UploadDropzone`, `UploadZone`, `FileCard`, `UploadQueueItem`, `UploadProgress` — shared react-dropzone/file-status compositions using exported `UploadStatus`.
- `CalendarSingle`, `CalendarRange`, `DatePicker`, `AgendaList` — react-day-picker compositions; agenda items use exported `AgendaItem`.

## Dialogs and feedback

- `Dialog`, `DialogTrigger`, `DialogContent`, `DialogClose`; `Modal`, `ModalTrigger`, `ModalContent`; `DrawerContent`; `ConfirmationDialog` — grouped Radix dialog family. Provide accessible titles/descriptions through their contracts.
- `StatusBadge` — badge with optional icon/label.
- `Alert` — title required; `variant="info"` (`success|warning|danger`) and optional action.
- `EmptyState` — title/description required; optional icon/action. `NoResults`, `NoData`, `NoContent` provide default icons. `ErrorState` optionally creates a retry action.
- `Skeleton`, `SkeletonText` (`lines=3`), `SkeletonCard` (`hasMedia=false`), `SkeletonTable` (`rows=5`, `columns=4`), `Spinner` (`label="Loading"`), `Progress` (bounded numeric value and label), `LiveRegion` (`politeness="polite"`), `LoadingOverlay` (`label="Loading"`, `isVisible=true`).

## Usage

```tsx
import { Alert } from "@/components/feedback";
import { PageContainer, PageHeader } from "@/components/layout";

<PageContainer>
  <PageHeader title="Library" />
  <Alert title="Draft saved">Your local changes are available on this device.</Alert>
</PageContainer>;
```

Prefer category imports, semantic variants, visible labels, and feature-local wrappers for domain-specific behavior. Do not add domain props to shared primitives.

# State Management

## Decision hierarchy

Use the narrowest state owner:

1. URL for shareable navigation state.
2. Server data source for persistent remote state.
3. Form state for editable input.
4. Local component state for ephemeral interaction.
5. Context for stable subtree-wide UI state.
6. External client store only when the preceding options cannot meet the requirement.

Do not duplicate server data or URL state in a global store.

## URL state

Search, filters, sorting, pagination, selected tabs, and other linkable views should use typed query parameters. Parse and validate at the route boundary. Use replace for transient refinements and push for meaningful navigation history.

## Server state

Until TanStack Query is adopted, load initial data in server components and use the project-approved mutation path. When adopted:

- Define query keys through feature query-key factories.
- Place query options and mutations under each feature's API module.
- Set stale time intentionally.
- Invalidate the narrowest affected keys after mutation.
- Use optimistic updates only when rollback behavior is safe and tested.
- Never use the cache as a permanent client database.

## Local and shared UI state

Use `useState` or `useReducer` for local transitions. Context is appropriate for theme, sidebar, modal coordination, or other stable cross-tree concerns. Split state and dispatch contexts when rerender pressure is material.

## Recommended reusable hooks

- `useSidebar()` — responsive navigation state.
- `useTheme()` — approved theme API.
- `useSearch()` — debounced input synchronized with URL state.
- `usePagination()` — typed page state and boundary rules.
- `useToast()` — feedback through the shared provider.
- `useModal()` — controlled dialog coordination.
- `useCalendar()` — date-range interaction, not date business rules.
- `useContent()` — feature data facade after the API contract exists.
- `useUpload()` — upload queue and lifecycle.

Hooks must hide mechanics, not product policy. A hook is warranted when behavior repeats or needs isolated testing.

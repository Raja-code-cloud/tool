# Hooks Guide

## When to create a hook

Create a hook when stateful React behavior is reused, when a complex interaction needs a testable boundary, or when a provider requires a safe consumer API. Do not create hooks merely to wrap one function call or hide straightforward render logic.

## Contract standards

- Name hooks `useX` and files `use-x.ts`.
- Accept a typed options object when arguments may grow.
- Return the smallest stable API consumers need.
- Prefer explicit status unions over several contradictory booleans.
- Keep effects synchronized with external systems and clean them up.
- Preserve exhaustive dependency lists; restructure code instead of disabling lint rules.
- Throw a clear error when a required provider is absent.

## Recommended ownership

- `hooks/`: generic browser and application-shell behavior (sidebar, toast, pagination, theme).
- `app/(dashboard)/<route>/_components/`: route-local domain hooks such as `use-wizard-state.ts` (**current implementation**).
- `features/<feature>/hooks/`: target convention for domain behavior in greenfield modules.
- Component-local file: behavior used by one component only.

## Planned hook boundaries

- `useUpload`: validation, queue, cancellation, progress, retry.
- `useSidebar`: open state, responsive mode, persistence.
- `useTheme`: read and set approved themes without exposing provider internals.
- `useSearch`: debouncing and URL synchronization.
- `usePagination`: page transitions and bounds.
- `useToast`: typed feedback requests.
- `useModal`: controlled modal state and focus-safe coordination.
- `useCalendar`: selection interaction and locale display.
- `useContent`: content query/mutation facade after contracts exist.

## Browser APIs

Shared hooks around storage, media queries, observers, and event listeners must support server rendering, avoid hydration mismatches, clean up subscriptions, and tolerate unavailable APIs.

## Testing

Test externally observable transitions, cancellation, cleanup, error paths, and provider misuse. For data hooks, mock the API boundary rather than implementation details of the query library.


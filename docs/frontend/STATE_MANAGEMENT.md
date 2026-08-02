# State management

## Current implementation

The frontend has no global third-party state store. State is divided by lifetime:

- Server components compose static route/layout output.
- Client feature hooks own filters, selections, forms, and mock workflow state.
- `SidebarProvider`, `AppToastProvider`, and `ThemeProvider` expose narrow context state.
- Pagination is encapsulated by a shared hook.
- Constants and mock repositories provide initial/domain data; services provide the feature-facing operations.
- The upload workflow persists its draft to browser `localStorage`. That draft is device/browser-local and must be guarded for client execution.

No frontend API routes, Server Actions, network fetch layer, auth/session state, ISR, or remote cache is implemented.

## Boundaries

Keep transient input nearest its component. Lift state only to the feature hook that coordinates it. Use context for truly shell-wide behavior, not feature records. Components call services; services call repositories. Do not let views import mock data directly when a service exists.

## Future API integration strategy (not implemented)

Introduce HTTP repository implementations behind the existing service contracts. Add explicit loading/error/cancellation behavior, map transport DTOs to domain types, and decide server-versus-client fetching per route. Authentication, cache policy, mutations, optimistic updates, and revalidation require separate product and security decisions; none should be inferred from the current mocks.

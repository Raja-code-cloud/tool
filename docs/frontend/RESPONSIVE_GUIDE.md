# Responsive guide

The Tailwind v4 breakpoints are exact CSS values:

- Mobile: below `48rem`
- `tablet`: `48rem` (768px at the default root size)
- `desktop`: `64rem` (1024px)
- `wide`: `90rem` (1440px)

Prefer these named breakpoints over arbitrary media values.

## Verified shell behavior

The application shell becomes a sidebar/content grid at `desktop`. The header hides search below `tablet` and shows its compact title there. Page vertical padding is `1rem` on mobile, `1.5rem` from tablet, and `2rem` from desktop. Horizontal `page-gutter` follows the same values. The full sidebar and its compact/mobile controls are coordinated by `SidebarProvider`/`WorkspaceShell`.

## Feature patterns

Headers stack actions on narrow screens and align them horizontally when space allows. Card headers similarly change at `tablet`. Tables use horizontal overflow; a primary column may remain sticky. Toolbars and actions wrap. Content is capped at `90rem`, reading content at `55rem`.

Test narrow mobile, 48rem, 64rem, and 90rem boundaries, plus long labels and zoom. Do not equate pointer capability with viewport width.

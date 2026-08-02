# Tailwind Standards

## Token-first styling

Use semantic tokens exposed through Tailwind and CSS variables: background, foreground, card, popover, primary, secondary, muted, accent, destructive, border, input, ring, and data-visualization tokens. Do not introduce raw hex values or one-off colors in components.

Dark mode is the primary visual target, but every semantic token must have an accessible light-mode counterpart. Theme selection belongs on the root element through the project-approved theme provider.

## Class usage

- Use utilities directly for local layout and styling.
- Use `cn()` for conditional classes.
- Use CVA for reusable semantic variants.
- Follow the project formatter's canonical class ordering.
- Avoid arbitrary values when a token or scale value exists.
- Do not use `@apply` to recreate components; reserve it for narrow global base patterns.
- Do not construct class names dynamically from partial strings because Tailwind cannot reliably detect them.

## Responsive implementation

Build mobile-first. Product behavior follows the documented ranges: mobile below 768 px, tablet at 768–1023 px, compact desktop at 1024–1439 px, and full desktop at 1440 px and above. Configure named Tailwind screens to express these ranges consistently rather than relying on framework defaults. Prefer fluid grids, wrapping, `minmax`, and container-aware composition over duplicated desktop/mobile trees.

## Spacing and layout

Use the established spacing scale. Repeated page gutters, vertical rhythm, control heights, radii, and elevations must become shared tokens or layout components. Prefer `gap` over sibling margins. Avoid absolute positioning for primary layout.

## Typography

Use Inter with `Segoe UI` and system fallbacks; use JetBrains Mono with `Cascadia Code` and monospace fallbacks for code/data. Define semantic roles for Display (32/40, 650), H1 (24/32, 650), H2 (20/28, 600), H3 (16/24, 600), Body (14/22, 400), Small (12/18, 400), Label (12/16, 600), and Data (13/20, 500). Apply tabular numbers to metrics, counters, calendars, and tables. Do not create local font sizes when an existing role communicates the same hierarchy.

## State styling

Every interactive component defines hover, active, focus-visible, disabled, loading, invalid, and selected states as applicable. Never remove outlines without an equivalent visible focus ring.


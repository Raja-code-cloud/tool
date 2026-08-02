# Accessibility guide

## Verified implementation

- Root language is English; a skip link targets the shell's focusable `#main-content`.
- Radix primitives provide keyboard/focus semantics for menus, dialogs, selects, checks, switches, and radio groups.
- Global `:focus-visible` styling and semantic foreground/background tokens are defined.
- Forms connect labels, descriptions, errors, required and invalid state.
- Tables use captions, column headers, and status-like empty states.
- Charts expose frame/legend/data-table compositions for nonvisual alternatives.
- Spinners, progress, alerts, live regions, empty/error states, and reduced-motion handling are available.
- Icon-only and dismiss controls in shared components carry labels where implemented.

## Gaps and review obligations

These primitives do not prove every route meets WCAG. There is no verified automated accessibility test suite. Check page heading order, dialog names/descriptions, chart alternatives, focus after navigation, status announcements, color contrast in both themes, keyboard-only operation, zoom/reflow, and meaningful image alt text. Do not use placeholder text as a label or communicate state by color alone.

Test recommendations are recommendations, not claims about current CI: combine keyboard/screen-reader review with axe-based automation and browser contrast/reflow checks.

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

## Automated testing

The frontend includes automated accessibility checks:

| Layer               | Tool                   | Location                                                         |
| ------------------- | ---------------------- | ---------------------------------------------------------------- |
| Unit/integration    | `vitest-axe`           | `tests/utils/axe.ts`, `tests/integration/accessibility.test.tsx` |
| E2E                 | `@axe-core/playwright` | `tests/e2e/accessibility.spec.ts`                                |
| Component isolation | Storybook a11y addon   | `.storybook/main.ts` (local only; not CI-gated)                  |

Helpers filter **critical** and **serious** axe violations. CI runs Vitest accessibility integration tests; Playwright a11y specs run locally via `npm run test:e2e`.

## Gaps and review obligations

Automated tests do not prove every route meets WCAG. Manual review is still required for page heading order, dialog names/descriptions, chart alternatives, focus after navigation, status announcements, color contrast in both themes, keyboard-only operation, zoom/reflow, and meaningful image alt text. Do not use placeholder text as a label or communicate state by color alone.

Combine keyboard/screen-reader review with axe-based automation and browser contrast/reflow checks.

## Related documentation

- [Testing guide](./TESTING_GUIDE.md)
- [UX audit](./UX_AUDIT.md)
- [Lighthouse report](./LIGHTHOUSE_REPORT.md)

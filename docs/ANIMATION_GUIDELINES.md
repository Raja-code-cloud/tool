# Animation Guidelines

## Principles

Motion clarifies cause, hierarchy, continuity, or status. It must not delay work or exist only as decoration. Prefer CSS transitions for simple state changes and Framer Motion for coordinated layout, presence, gesture, or sequence behavior.

## Timing

- Hover and color transitions: 100–150 ms.
- Menus and tooltips: 120–160 ms fade/scale from 98%.
- Dialogs: 160–200 ms fade/scale.
- Drawers: 180–220 ms slide.
- Optional page-content fade: 120–180 ms while the navigation shell remains stable.

Use approved easing tokens. Entrances ease out; exits ease in; direct manipulation tracks input.

## Patterns

- Animate opacity and transforms when possible.
- Avoid animating layout properties that trigger repeated reflow.
- Keep loading skeleton motion subtle.
- Do not animate every item in large data sets.
- Do not stagger lists.
- Use stable layout identifiers only where continuity is unambiguous.
- Ensure exit animations cannot block navigation or submission.

## Reduced motion

Use `prefers-reduced-motion` and Framer Motion's reduced-motion support. Remove parallax, large translations, continuous motion, and elaborate stagger. Preserve state communication through instant changes or brief opacity transitions.

## Accessibility and performance

Motion must not flash, trap attention, or communicate essential information without another cue. Animation code for heavy, infrequent experiences may be dynamically loaded. Test transitions on lower-powered devices and during concurrent loading.

## Ownership

Shared durations, easings, and variants belong in a central motion module. Components may select approved patterns but must not invent new motion language without design review.

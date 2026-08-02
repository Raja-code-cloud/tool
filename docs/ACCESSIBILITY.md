# Accessibility

Target WCAG 2.2 AA. Accessibility is part of acceptance criteria, not a post-release audit.

## Semantics

- Use landmarks, headings in logical order, lists, tables, buttons, and links according to meaning.
- Use a button for actions and a link for navigation.
- Every control has an accessible name.
- Use ARIA only when native semantics cannot express the interaction.

## Keyboard

All functionality must work without a pointer. Maintain visible focus, logical tab order, and expected keys for composite widgets. Never add positive `tabIndex`. Provide skip navigation for persistent application chrome.

## Focus management

- Move focus into dialogs and return it to the trigger on close.
- After route or major view changes, place focus according to the product navigation model.
- On failed form submission, focus the error summary or first invalid field.
- Do not unexpectedly steal focus during background updates.

## Screen readers

Associate errors and descriptions with controls. Announce asynchronous outcomes through appropriately scoped live regions. Decorative icons use `aria-hidden`; icon-only controls require explicit labels. Avoid repetitive announcements from frequently updating regions.

## Visual access

- Meet 4.5:1 contrast for normal text and 3:1 for large text and meaningful UI boundaries.
- Do not communicate status by color alone.
- Support zoom to 200% and reflow at 320 CSS pixels without loss of function.
- Preserve focus visibility in every theme and state.

## Motion and media

Respect `prefers-reduced-motion`. Disable nonessential motion and replace spatial transitions with instant or subtle opacity changes. Provide captions or transcripts for meaningful media.

## Verification

Check keyboard-only operation, focus order, accessible names, zoom/reflow, high-contrast behavior, and automated accessibility rules. Validate critical workflows with a screen reader; automated tools are insufficient by themselves.

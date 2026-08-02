# Reusable Patterns

## Forms

Use React Hook Form for client forms and Zod as the validation contract. Infer form types from schemas. Validate at every trust boundary, including the server; client validation improves UX but is not authorization.

- Build accessible field compositions around label, control, description, and error.
- Show field errors near controls and a summary when submission can fail across many fields.
- Disable duplicate submission while preserving readable values.
- Preserve user input on recoverable failures.

## API layer

Keep transport under `lib/api` and feature contracts under `features/<feature>/api`.

- A base client handles URL resolution, headers, serialization, cancellation, and normalized errors.
- Feature functions expose domain operations, not raw endpoint mechanics.
- Parse untrusted responses when runtime certainty matters.
- Pass `AbortSignal` through requests.
- Never access environment secrets from client modules.

## Error handling

Normalize failures into typed categories: validation, authentication, authorization, not found, conflict, rate limit, network, and unknown. Route error boundaries handle unrecoverable rendering errors. Inline feedback handles recoverable actions. Messages must explain impact and a next action without leaking internals.

## Loading and skeletons

- Use route `loading.tsx` for navigation latency and local Suspense boundaries for independent regions.
- Preserve layout dimensions to prevent shifts.
- Skeletons mirror the final geometry, not every decorative detail.
- Use progress indicators for determinate uploads and spinners only for compact indeterminate actions.
- Respect reduced motion.

## File uploads

Treat uploads as a state machine: idle, validating, queued, uploading, paused/retrying where supported, complete, and failed. Validate type, size, count, and filename before transport, then validate again server-side. Support cancellation and per-file progress. Use direct or multipart uploads through a backend-issued capability; never expose storage credentials.

## Tables

Use TanStack Table as a headless engine. Define typed column factories and reusable cells. Keep sorting, filtering, and pagination server-driven for large data. Preserve query state in the URL. Provide caption/accessible name, keyboard-operable controls, loading, empty, error, and narrow-screen behavior. Use virtualization only after measurement.

## Charts

Wrap the approved chart library behind shared chart components. Use semantic tokens, visible legends, formatted tooltips, and a text/table alternative for essential information. Do not rely on color alone. Lazy-load chart code below the fold.

## Feedback states

Empty states explain what is absent and offer one relevant action. Toasts confirm transient outcomes; persistent or blocking failures remain inline. Confirmation dialogs state the object and consequence explicitly.


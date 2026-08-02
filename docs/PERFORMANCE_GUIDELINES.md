# Performance Guidelines

## Rendering strategy

- Prefer Server Components to reduce client JavaScript.
- Keep client boundaries small and avoid provider wrappers at the application root unless truly global.
- Stream independent slow regions through Suspense.
- Avoid client-side waterfalls by initiating independent requests together.

## Code splitting

- Use route-level splitting provided by Next.js.
- Use dynamic imports for large editors, charting, media tools, and infrequently opened workflows.
- Do not dynamically import small, frequently used components.
- Load browser-only libraries with `ssr: false` only when they cannot execute safely on the server.

## Assets

- Use `next/image` for raster content with known dimensions and correct `sizes`.
- Prefer SVG icon components for interface icons.
- Use `next/font` and limit families, weights, and character subsets.
- Avoid autoplaying or eagerly loading nonessential media.

## Memoization

Memoize only after identifying expensive work or referential churn. `useMemo`, `useCallback`, and `memo` are not defaults. Keep props stable through good component boundaries before adding memoization.

## Large collections

Use server pagination by default. Consider virtualization for measured rendering bottlenecks in long, interactive lists. Maintain keyboard navigation, focus, row identity, and screen-reader usability when virtualizing.

## Bundle discipline

- Import package entry points that support tree shaking.
- Avoid broad barrel imports from large libraries.
- Keep server-only dependencies out of client graphs.
- Inspect bundle changes when adding a substantial dependency.
- Prefer platform APIs or existing dependencies for small utilities.

## Runtime quality

Set explicit performance budgets when baseline measurements exist. Track Core Web Vitals, layout shift, interaction latency, route payloads, and client bundle growth. Performance claims require production-like measurement, not development-mode impressions.

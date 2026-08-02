# Performance guide

## Verified implementation

- App Router provides route-level code splitting.
- Feature views use dynamic imports for heavier client sections.
- `next.config.ts` enables `optimizePackageImports` for `lucide-react`, `recharts`, and `framer-motion`.
- `next/font` loads Inter with `display: "swap"`.
- Server components remain the default outside interactive boundaries.
- The production config enables React strict mode and removes the powered-by header.

There is no verified remote cache, ISR/revalidation policy, Suspense streaming implementation, frontend request cache, or image CDN configuration.

## Recommendations, not current behavior

Measure route bundles and Web Vitals before optimization. Keep charting, calendar, and upload dependencies out of unrelated routes; narrow client boundaries; virtualize only measured large lists; and add explicit request/cache policies when API integration exists. Validate dynamic imports do not hide important content from server output and avoid adding memoization without evidence.

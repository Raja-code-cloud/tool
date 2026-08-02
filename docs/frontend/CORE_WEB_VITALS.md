# Core Web Vitals Assessment

## Executive Summary

No production URL, completed production build, Lighthouse trace, or real-user monitoring data was available. The values below are engineering estimates based on static architecture and must not be treated as measured results.

## Estimated Metrics

| Metric | Estimated range |  Target | Risk   |
| ------ | --------------: | ------: | ------ |
| TTFB   |       0.3–0.9 s |  ≤0.8 s | Medium |
| FCP    |       1.2–2.4 s |  ≤1.8 s | Medium |
| LCP    |       1.8–3.6 s |  ≤2.5 s | High   |
| CLS    |       0.03–0.15 |   ≤0.10 | Medium |
| INP    |      180–400 ms | ≤200 ms | High   |

Ranges assume a production CDN, mid-tier mobile device, throttled mobile network, cold navigation, and current mock data. Real API latency may materially worsen TTFB/LCP.

## FCP

Helpful factors:

- Server-rendered route structure.
- Local Next.js font optimization.
- Small root redirect.

Risks:

- Shared client shell and global providers.
- CSS animation package and broad component-library imports.
- No measured critical CSS or JavaScript execution profile.

## LCP

Likely LCP candidates are page headings, summary cards, editor panels, or large skeleton/content containers rather than hero imagery.

Risks:

- Hydration and client-side feature computation can delay meaningful completion.
- Large analytics/chart and editor routes may increase main-thread work.
- Real data fetching is not yet represented.

## CLS

Helpful factors:

- Skeletons generally reserve height.
- Preview images have width and height.
- `next/font` reduces font-layout instability.

Risks:

- Theme changes after hydration can alter colors and potentially component rendering.
- Dynamically loaded panels need route-by-route geometry verification.
- Responsive drawers, banners, status messages, and uploaded-media previews may shift content.

## INP

This is the highest runtime risk.

- Large client trees hydrate on every dashboard route.
- Filters trigger multiple synchronous analytics derivations and chart updates.
- Framer Motion, drag interactions, large grids, and editor state can create long tasks.
- No interaction trace, scheduler profiling, virtualization threshold, or RUM exists.

## TTFB

Current pages appear mostly static/mock-driven, so CDN TTFB should be acceptable. Once authenticated APIs are added, TTFB depends on region placement, session validation, server waterfalls, and cache policy. Independent requests should start concurrently and stream behind Suspense boundaries.

## Critical Findings

1. There is no measured CWV baseline.
2. The production build is not currently a trusted measurement artifact.
3. INP and LCP have material architectural risk from broad client boundaries.

## High Priority

1. Produce a successful production build and test representative routes with Lighthouse mobile.
2. Add `useReportWebVitals` or an equivalent supported RUM pipeline.
3. Break down metrics by route, device, connection, and release.
4. Profile interactions on analytics filters, scheduler drag/move, content grids, and AI Studio editing.

## Medium Priority

1. Add local Suspense/streaming with stable fallbacks.
2. Reduce initial client JavaScript and defer noncritical animation/chart code.
3. Set explicit layout dimensions for all future media and async regions.
4. Track long tasks and total blocking time as diagnostics for INP.

## Low Priority

1. Add pre-release synthetic testing across desktop and mobile profiles.
2. Record soft-navigation metrics when framework/browser support is reliable.

## Quick Wins

- Add Web Vitals reporting.
- Add Lighthouse CI budgets.
- Record route bundle sizes.
- Verify all skeletons match final geometry.

## Long-Term Improvements

- Use p75 field data as the release authority.
- Set route budgets for LCP, INP, CLS, JavaScript, and long tasks.
- Correlate regressions with deployment versions and feature flags.

## Production Readiness Score

**55/100 — CWV readiness is unverified until field and production synthetic data exist.**

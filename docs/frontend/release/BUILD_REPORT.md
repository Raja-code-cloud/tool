# Build Report — Cloud Content Hub Frontend RC Audit

**Audit date:** 2026-08-03  
**Commit:** `172fcc4f87a4bf0853c9e34f0585978a4a28f4a6`  
**Build command:** `npm run build` → `next build`

---

## Build Status

| Field                          | Value                                                                |
| ------------------------------ | -------------------------------------------------------------------- |
| **Result (this audit)**        | **FAIL** — `node_modules` corruption; `next` CLI unavailable         |
| **Last verified build**        | 2026-08-02 (dependency audit) — **PASS**                             |
| **Build time (last verified)** | ~94s compile (Lighthouse doc notes validation worker exit afterward) |
| **Output mode**                | Standard Next.js (not `output: "standalone"`)                        |
| **React strict mode**          | Enabled                                                              |
| **`poweredByHeader`**          | Disabled                                                             |

---

## Generated Routes

| Route              | Page file                                  | Status                       |
| ------------------ | ------------------------------------------ | ---------------------------- |
| `/`                | `app/page.tsx`                             | Redirect → `/dashboard`      |
| `/dashboard`       | `app/(dashboard)/dashboard/page.tsx`       | Static                       |
| `/content-library` | `app/(dashboard)/content-library/page.tsx` | Static                       |
| `/upload`          | `app/(dashboard)/upload/page.tsx`          | Static                       |
| `/ai-studio`       | `app/(dashboard)/ai-studio/page.tsx`       | Static                       |
| `/scheduler`       | `app/(dashboard)/scheduler/page.tsx`       | Static                       |
| `/calendar`        | `app/(dashboard)/calendar/page.tsx`        | Static (placeholder content) |
| `/analytics`       | `app/(dashboard)/analytics/page.tsx`       | Static                       |
| `/social-accounts` | `app/(dashboard)/social-accounts/page.tsx` | Static                       |
| `/settings`        | `app/(dashboard)/settings/page.tsx`        | Static                       |

**Layouts:** Root (`app/layout.tsx`), dashboard group (`app/(dashboard)/layout.tsx`), loading (`loading.tsx`), error boundary (`error.tsx`).

**Total static segments (last verified):** 13

---

## Bundle Sizes (Last Verified Baseline)

From 2026-08-02 production build analysis:

| Segment      | First Load JS                             |
| ------------ | ----------------------------------------- |
| **Shared**   | 103 kB                                    |
| `/scheduler` | **271 kB** (largest)                      |
| `/analytics` | ~260 kB (estimated from feature weight)   |
| `/upload`    | ~250 kB (estimated; dynamic step imports) |
| `/dashboard` | **221 kB** (smallest feature route)       |
| `/settings`  | ~230 kB (estimated)                       |

_Exact per-route figures require successful `next build` with bundle analyzer on audit host._

---

## Largest Chunks (Observed Patterns)

| Chunk source  | Drivers                                                                       |
| ------------- | ----------------------------------------------------------------------------- |
| Shared layout | `WorkspaceShell`, Radix menus, theme provider, Framer Motion page transitions |
| `/scheduler`  | Calendar views, `react-day-picker`, queue panel, analytics widget             |
| `/analytics`  | Recharts (`LineChart`, `PieChart`, `AreaChart`), custom bar charts            |
| `/upload`     | Dynamic step imports, `react-dropzone`, file validation                       |
| `/ai-studio`  | Multi-panel editor, suggestions drawer                                        |

---

## Largest Dependencies

| Dependency         | Approx. impact                 | Mitigation                                    |
| ------------------ | ------------------------------ | --------------------------------------------- |
| `framer-motion`    | High — 20+ route components    | `optimizePackageImports`                      |
| `recharts`         | High — analytics route         | Package import optimization + route splitting |
| `lucide-react`     | Medium — icons app-wide        | Named imports + optimization                  |
| `react-day-picker` | Medium — scheduler/calendar    | Route-scoped                                  |
| `@radix-ui/*`      | Medium — modular per-primitive | Tree-shaken per import                        |

---

## Tree Shaking Observations

**Implemented:**

```typescript
// next.config.ts
experimental: {
  optimizePackageImports: ["lucide-react", "recharts", "framer-motion"],
},
```

**Effective patterns:**

- Named icon imports from `lucide-react` (project convention)
- Per-primitive Radix imports (not barrel `@radix-ui/react`)
- Category barrel exports in `components/` for intentional public API

**Opportunities:**

- Recharts: import individual chart primitives vs barrel where possible
- Lazy-load below-fold Framer Motion panels
- Upload wizard steps already use dynamic imports

---

## Code Splitting Observations

| Pattern                    | Location                                                                               |
| -------------------------- | -------------------------------------------------------------------------------------- |
| App Router route splitting | Automatic per `app/(dashboard)/*/page.tsx`                                             |
| Dynamic step imports       | `upload/_components/upload-wizard-view.tsx`                                            |
| Dynamic dialogs/panels     | Content preview, suggestions drawer, account details                                   |
| Client boundary            | Most feature views are `"use client"` — increases shared client bundle                 |
| Missing route loading      | Only dashboard-level and settings `loading.tsx`; other routes rely on in-view spinners |

**Risk:** Shared `WorkspaceShell` client tree loads on every dashboard route, inflating initial JS for all pages.

---

## Build Warnings

| Warning                           | Source                                 | Severity           |
| --------------------------------- | -------------------------------------- | ------------------ |
| `next lint` deprecation           | Next.js 16 migration                   | Low                |
| Node engine mismatch              | Audit host 22.13.1 vs required 22.22.1 | Medium             |
| No `.next` artifact on audit host | Environment failure                    | Blocker for deploy |
| Source maps in release tarball    | KI-051                                 | Medium (ops)       |

---

## Security Headers (Build Output)

Applied via `next.config.ts` → `buildSecurityHeaders()`:

- Content-Security-Policy (production: no `unsafe-eval`)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy, Permissions-Policy, COOP, CORP

---

## CI Build Pipeline

From `.github/workflows/build.yml`:

1. Quality job: format, typecheck, lint, test:coverage
2. Production build job: `npm run build`
3. Artifact: `.next/`, `package.json`, `package-lock.json`, `next.config.ts` (14-day retention)

---

## Recommendations

| Priority | Action                                                                |
| -------- | --------------------------------------------------------------------- |
| P0       | Complete successful `npm run build` on Node 22.22.1 CI runner         |
| P1       | Run `@next/bundle-analyzer` for fresh per-route sizes                 |
| P1       | Add route-level `loading.tsx` for heavy routes (analytics, scheduler) |
| P2       | Evaluate `output: "standalone"` for deployment adapter (KI-050)       |
| P2       | Restrict release artifact access (source maps — KI-051)               |

---

_Build metrics marked "last verified" sourced from 2026-08-02 audit; this audit could not regenerate due to environment failure._

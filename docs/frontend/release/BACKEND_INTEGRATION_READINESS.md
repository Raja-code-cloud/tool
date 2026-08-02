# Backend Integration Readiness — Cloud Content Hub Frontend RC Audit

**Audit date:** 2026-08-03  
**Commit:** `172fcc4f87a4bf0853c9e34f0585978a4a28f4a6`

---

## Executive Summary

The frontend is **architecturally prepared** for backend integration via a repository pattern, typed DTOs, and a configurable HTTP client. **Runtime integration is inactive:** all product features consume in-memory mock repositories. Authentication, OpenAPI codegen, HTTP retry, and offline handling are **not implemented**.

**Readiness score:** 30/100 for production backend connectivity

---

## Integration Checklist

| Capability | Status | Notes |
| ---------- | ------ | ----- |
| Mock API layer | **Active** | `lib/adapters/mock-repositories.ts` |
| DTO compatibility | **Partial** | `lib/api/types.ts` defines frontend DTOs; not generated from OpenAPI |
| OpenAPI compatibility | **Not integrated** | Backend spec exists; no frontend codegen |
| Authentication abstraction | **Missing** | Mock user in `constants/workspace.ts` |
| Environment variables | **Implemented** | Zod-validated in `lib/config/env.ts` |
| API client | **Scaffolded** | `lib/api/client.ts`; disabled without base URL |
| Error handling | **Partial** | `ApiError`, `ErrorState`; no global HTTP interceptor |
| Retry handling | **Missing** | Manual `onRetry` only |
| Loading states | **Implemented** | Route loading, skeletons, overlays |
| Offline behavior | **Missing** | No `navigator.onLine` handling |

---

## Mock API Layer

### Architecture

```
UI Components
    ↓
Feature state hooks (app/(dashboard)/*/_components/use-*-state.ts)
    ↓
Services (lib/services/workspace-services.ts)
    ↓
Repositories (lib/adapters/mock-repositories.ts)
    ↓
Static constants (constants/*)
```

### Exported services (`lib/services/index.ts`)

| Service | Mock repository |
| ------- | --------------- |
| `contentService` | `mockContentRepository` |
| `schedulerService` | `mockSchedulerRepository` |
| `socialAccountService` | `mockSocialAccountRepository` |
| `aiStudioService` | `mockAiStudioRepository` |
| `dashboardService` | `mockDashboardRepository` |
| `analyticsService` | `mockAnalyticsRepository` |
| `settingsService` | `mockSettingsRepository` |
| `workspaceService` | `mockWorkspaceRepository` |

**No feature code calls HTTP today.**

### MSW (tests only)

- `tests/integration/msw-foundation.test.ts`
- Not wired into application runtime

---

## DTO Compatibility

**File:** `lib/api/types.ts`

| Type | Purpose |
| ---- | ------- |
| `ContentItemDto` | Content library items |
| `ScheduledPostDto` | Scheduler posts |
| `AnalyticsPostDto` | Analytics rows |
| `PaginatedResponse<T>` | List pagination |
| `ListQueryParams` | Query filters |
| `ApiRequestConfig` | HTTP request options |
| `ApiResponse<T>` | Generic response wrapper |

**Gap:** DTOs are hand-maintained. Backend OpenAPI schema (`docs/backend/api-implementation/OPENAPI.md`, `backend/src/cloud_content_hub/api/openapi.py`) is not consumed by the frontend build.

**Recommendation:** Add OpenAPI codegen step; align field names with backend Pydantic models before v1.1.0.

---

## OpenAPI Compatibility

| Item | Status |
| ---- | ------ |
| Backend OpenAPI generator | Present (`backend/.../openapi.py`) |
| Frontend generated client | **Absent** |
| Contract tests | **Absent** |
| API version header | Not implemented |

---

## Authentication Abstraction

| Item | Status |
| ---- | ------ |
| Login page | **None** |
| Session management | **None** |
| JWT / Bearer storage | **None** |
| Role-based access | **None** |
| Mock identity | `CURRENT_USER` in `constants/workspace.ts` |
| Sign-out behavior | Clears sensitive localStorage only |
| API 401 handling | Mapped in client; unused |

**Production mitigation (KI-020):** Deploy behind VPN, IP allowlist, or identity-aware proxy until auth ships.

---

## Environment Variables

**Validated by:** `lib/config/env.ts` (Zod)

| Variable | Required | Default | Purpose |
| -------- | -------- | ------- | ------- |
| `NODE_ENV` | No | runtime | development \| test \| production |
| `NEXT_PUBLIC_APP_ENV` | No | development | Logical app environment |
| `NEXT_PUBLIC_API_BASE_URL` | No | unset | Enables HTTP client when set |

**Template:** `.env.example` present at repository root.

**Activation path:**

```typescript
// lib/services/index.ts
export const apiClient = env.NEXT_PUBLIC_API_BASE_URL
  ? createApiClient({ baseUrl: env.NEXT_PUBLIC_API_BASE_URL })
  : createDisabledApiClient();
```

HTTP repository adapters are **reserved** but not wired to services.

---

## API Client

**File:** `lib/api/client.ts`

| Method | Supported |
| ------ | --------- |
| GET | Yes |
| POST | Yes |
| PUT | Yes |
| PATCH | Yes |
| DELETE | Yes |

| Feature | Status |
| ------- | ------ |
| Base URL configuration | Yes |
| Default headers | Yes |
| Injectable `fetchFn` (testing) | Yes |
| JSON parse/error mapping | Yes |
| 401 → unauthorized | Yes |
| Automatic retry | **No** |
| Request timeout | **No** |
| Request cancellation | **No** |

---

## Error Handling

| Layer | Implementation |
| ----- | -------------- |
| HTTP errors | `ApiError` with code + message |
| Route errors | `app/(dashboard)/error.tsx` → `ErrorState` |
| Feature errors | Toast + inline alerts |
| Client reporting | `reportClientError()` (redacted in prod) |
| Form validation | `FormErrorSummary`, field-level errors |

**Gap:** No centralized error boundary for API failures across services.

---

## Retry Handling

| Context | Retry |
| ------- | ----- |
| HTTP client | **None** |
| ErrorState UI | Manual `onRetry` callback |
| Upload queue | Per-item retry in UI |
| Service layer | **None** |

---

## Loading States

| Pattern | Location |
| ------- | -------- |
| Route skeleton | `app/(dashboard)/loading.tsx`, settings loading |
| Feature refresh | Spinners, `SkeletonCard`, `SkeletonTable` |
| AI operations | `LoadingOverlay` with phase text |
| Dynamic imports | Upload step fallbacks |
| Button loading | `ActionButton` loading prop |

---

## Offline Behavior

| Feature | Status |
| ------- | ------ |
| Online/offline detection | **Not implemented** |
| Offline UI banner | **Not implemented** |
| Queued mutations | **Not implemented** |
| Service worker / PWA | **Not implemented** |

Draft persistence in localStorage survives refresh but not cross-device sync (KI-011).

---

## Simulated Integrations (Not Real Backend)

| Feature | Simulation |
| ------- | ---------- |
| Social OAuth | Toast messages only (KI-031) |
| Scheduler publish | Mock notifications (KI-032) |
| AI Studio transforms | Deterministic mock (KI-033) |
| Analytics date filter | Fixed mock window (KI-034) |

---

## Readiness Roadmap

| Phase | Work |
| ----- | ---- |
| 1 | Wire `NEXT_PUBLIC_API_BASE_URL`; implement HTTP repository adapters |
| 2 | OpenAPI codegen + contract tests |
| 3 | Auth provider integration (session/JWT) |
| 4 | HTTP retry/timeout policy |
| 5 | Offline detection + graceful degradation |
| 6 | Replace mock constants with live data migration |

---

## Release Blockers (Backend)

| Blocker | Severity | RC acceptable? |
| ------- | -------- | -------------- |
| No real auth | High | Yes for internal staging with network controls |
| Mock-only data | High | Yes for UI validation RC |
| HTTP adapters inactive | Medium | Yes if documented |
| No OpenAPI sync | Medium | Yes for RC; required before GA |

---

*See also: `docs/frontend/DEVELOPER_GUIDE.md`, `docs/release/KNOWN_ISSUES.md` (KI-010 through KI-035)*

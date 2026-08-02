# Routers

All business routes are mounted under `/api/v1`. Health probes are unversioned.

## Health (`routers/v1/health.py`)

| Operation ID   | Method | Path      | Auth   |
| -------------- | ------ | --------- | ------ |
| `getHealth`    | GET    | `/health` | public |
| `getLiveness`  | GET    | `/live`   | public |
| `getReadiness` | GET    | `/ready`  | public |

## Assets (`routers/v1/assets.py`)

Prefix: `/api/v1/assets`

| Operation ID       | Method | Path            | Permission      | Handler key     |
| ------------------ | ------ | --------------- | --------------- | --------------- |
| `uploadAsset`      | POST   | `/upload`       | `assets:write`  | `upload_asset`  |
| `listAssets`       | GET    | ``              | `assets:read`   | `list_assets`   |
| `searchAssets`     | GET    | `/search`       | `assets:read`   | `search_assets` |
| `getAsset`         | GET    | `/{id}`         | `assets:read`   | `get_asset`     |
| `deleteAsset`      | DELETE | `/{id}`         | `assets:delete` | `delete_asset`  |
| `replaceAssetFile` | POST   | `/{id}/replace` | `assets:write`  | `replace_asset` |

## Content (`routers/v1/content.py`)

Prefix: `/api/v1/content`

| Operation ID        | Method | Path              | Permission         | Handler key                              |
| ------------------- | ------ | ----------------- | ------------------ | ---------------------------------------- |
| `generateContent`   | POST   | `/generate`       | `content:generate` | `generate_content`                       |
| `regenerateContent` | POST   | `/regenerate`     | `content:generate` | `regenerate_content`                     |
| `listContent`       | GET    | ``                | `content:read`     | `list_content`                           |
| `getContent`        | GET    | `/{id}`           | `content:read`     | `get_content`                            |
| `updateContent`     | PATCH  | `/{id}`           | `content:write`    | `create_content_version` + `get_content` |
| `deleteContent`     | DELETE | `/{id}`           | `content:delete`   | `delete_content`                         |
| `duplicateContent`  | POST   | `/{id}/duplicate` | `content:write`    | `duplicate_content`                      |
| `archiveContent`    | POST   | `/{id}/archive`   | `content:write`    | `archive_content`                        |

## Publishing (`routers/v1/publishing.py`)

Prefix: `/api/v1/publish`

| Operation ID             | Method | Path       | Permission          | Handler key                |
| ------------------------ | ------ | ---------- | ------------------- | -------------------------- |
| `createPublication`      | POST   | ``         | `publishing:write`  | `create_publication`       |
| `dispatchPublication`    | POST   | `/{id}`    | `publishing:write`  | `dispatch_publication`     |
| `listPublicationHistory` | GET    | `/history` | `publishing:read`   | `list_publication_history` |
| `cancelPublication`      | DELETE | `/{id}`    | `publishing:delete` | `cancel_publication`       |

## Scheduler (`routers/v1/scheduler.py`)

Prefix: `/api/v1/schedule`

| Operation ID     | Method | Path    | Permission        | Handler key       |
| ---------------- | ------ | ------- | ----------------- | ----------------- |
| `createSchedule` | POST   | ``      | `schedule:write`  | `create_schedule` |
| `listSchedules`  | GET    | ``      | `schedule:read`   | `list_schedules`  |
| `getSchedule`    | GET    | `/{id}` | `schedule:read`   | `get_schedule`    |
| `updateSchedule` | PATCH  | `/{id}` | `schedule:write`  | `update_schedule` |
| `cancelSchedule` | DELETE | `/{id}` | `schedule:delete` | `cancel_schedule` |

## Analytics (`routers/v1/analytics.py`)

Prefix: `/api/v1/analytics`

| Operation ID             | Method | Path         | Permission       | Handler key                |
| ------------------------ | ------ | ------------ | ---------------- | -------------------------- |
| `getAnalyticsDashboard`  | GET    | `/dashboard` | `analytics:read` | `get_analytics_dashboard`  |
| `listAnalyticsPosts`     | GET    | `/posts`     | `analytics:read` | `list_analytics_posts`     |
| `listAnalyticsPlatforms` | GET    | `/platforms` | `analytics:read` | `list_analytics_platforms` |
| `getAnalyticsPost`       | GET    | `/post/{id}` | `analytics:read` | `get_analytics_post`       |

## Notifications (`routers/v1/notifications.py`)

Prefix: `/api/v1/notifications`

| Operation ID           | Method | Path         | Permission             | Handler key              |
| ---------------------- | ------ | ------------ | ---------------------- | ------------------------ |
| `listNotifications`    | GET    | ``           | `notifications:read`   | `list_notifications`     |
| `markNotificationRead` | PATCH  | `/{id}/read` | `notifications:write`  | `mark_notification_read` |
| `deleteNotification`   | DELETE | `/{id}`      | `notifications:delete` | `delete_notification`    |

## Administration (`routers/v1/administration.py`)

Prefix: `/api/v1/admin`

| Operation ID           | Method | Path         | Permission   | Handler key               |
| ---------------------- | ------ | ------------ | ------------ | ------------------------- |
| `listAdminJobs`        | GET    | `/jobs`      | `admin:read` | `list_admin_jobs`         |
| `listAdminQueues`      | GET    | `/queues`    | `admin:read` | `list_admin_queues`       |
| `listAdminProviders`   | GET    | `/providers` | `admin:read` | `list_admin_providers`    |
| `getAdminSystemStatus` | GET    | `/system`    | `admin:read` | `get_admin_system_status` |

Admin routes treat `X-Workspace-ID` as optional; when absent the admin actor falls back to the authenticated user id for handler scoping.

## Router assembly

`routers/v1/router.py` exports:

- `api_router` — `/api/v1` business routes
- `root_router` — health probes + `api_router`

`bootstrap/api.py` includes `root_router` on the FastAPI application.

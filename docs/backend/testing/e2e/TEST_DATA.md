# Test Data

## Seed Bundle (`E2ESeedBundle`)

Each E2E test run seeds an isolated tenant via `seed_e2e_environment()`:

| Entity                  | Description                                           |
| ----------------------- | ----------------------------------------------------- |
| Organization            | Active commercial org                                 |
| Workspace               | Active workspace linked to org                        |
| User                    | Active user with email `e2e-{suffix}@example.test`    |
| Workspace membership    | Active membership for the user                        |
| AI provider + model     | `mock` / `mock-gpt`, enabled                          |
| Notification type       | `content.approved`                                    |
| Setting definitions     | `feature.ai_generation`, `system.maintenance_mode`    |
| Admin role              | Workspace-scoped `workspace_admin` with `admin:write` |
| Social platforms        | linkedin, facebook, instagram, x, medium, youtube     |
| Social accounts         | One connected healthy account per platform            |
| Metric definitions      | `{platform}.impressions` per platform                 |
| Article asset + version | Approved master article (v1)                          |
| Poster asset            | Launch poster metadata                                |
| Video asset             | Product video metadata                                |

## Deterministic Binary Fixtures

| Constant            | Purpose                 |
| ------------------- | ----------------------- |
| `SAMPLE_WEBP_BYTES` | Poster upload payloads  |
| `SAMPLE_PNG_BYTES`  | Image contract tests    |
| `SAMPLE_TEXT_BYTES` | Master article markdown |
| `SAMPLE_MP4_BYTES`  | Video upload payloads   |

## Permission Bundles

| Helper                 | Permissions                                  |
| ---------------------- | -------------------------------------------- |
| `WORKFLOW_PERMISSIONS` | Full workflow read/write/generate/admin read |
| `ADMIN_PERMISSIONS`    | Wildcard + admin read/write                  |

## Idempotency Keys

All mutating workflow tests use deterministic idempotency keys prefixed with `e2e-` to support safe reruns within a single database session.

## Publication Target Approval

Scheduling tests call `approve_publication_target()` to transition targets to `approved` because creation defaults to `pending`.

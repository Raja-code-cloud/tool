# Model Overview

All **86** approved tables are implemented as SQLAlchemy 2.x declarative models under `infrastructure/database/models/`. Each file exports one mapped class; junction tables use composite primary keys where the schema specifies `(role_id, permission_id)` style keys.

## Domain inventory

| Domain                   | Count | Key models                                                           |
| ------------------------ | ----: | -------------------------------------------------------------------- |
| Identity & tenancy       |    11 | `User`, `Organization`, `Workspace`, `Role`, `Permission`            |
| Projects & content       |    24 | `ContentAsset`, `Article`, `Video`, `ContentVersion`, `Project`      |
| AI generation            |     8 | `AIProvider`, `AIModel`, `AIGenerationRequest`, `AIGenerationOutput` |
| Social connections       |     7 | `SocialPlatform`, `SocialAccount`, `OAuthTokenVault`                 |
| Publishing & scheduling  |     8 | `Publication`, `PublicationSchedule`, `PublishingJob`                |
| Notifications            |     5 | `NotificationType`, `Notification`, `NotificationDelivery`           |
| Settings                 |     2 | `SettingDefinition`, `Setting`                                       |
| Analytics                |     5 | `MetricDefinition`, `MetricObservation`, `AnalyticsSnapshot`         |
| Usage & billing          |     8 | `UsageDimension`, `UsageEvent`, `Subscription`, `BillingEvent`       |
| Reliability & operations |     8 | `AuditLog`, `OutboxEvent`, `BackgroundJob`, `DataExport`             |

## Table shape categories

### Global catalog / principal (unscoped)

`users`, `organizations`, `ai_providers`, `social_platforms`, `permissions`, `notification_types`, `setting_definitions`, `usage_dimensions`, `metric_definitions`

### Organization-scoped

`organization_memberships`, `subscriptions`, `subscription_items`, `billing_customers`, `billing_events`, `quota_policies`, `quota_periods`

### Workspace-scoped (operational tenant)

All tables with required `workspace_id`: content, social accounts, publishing, notifications, analytics facts, etc.

Every workspace-scoped parent carries:

```python
UniqueConstraint("workspace_id", "id", name="uq_<table>__workspace_id_id")
```

### Subtype tables (asset_id PK)

`articles`, `videos`, `posters`, `thumbnails` — primary key is `asset_id` FK to `content_assets`.

### Junction / assignment tables

`role_permissions`, `membership_roles`, `collection_items`, `asset_tags`, `project_members`, etc. Composite PKs; `CASCADE` where schema specifies hard-delete with parent.

### Immutable / append-only

`content_versions`, `audit_logs`, `usage_events`, `publishing_attempts`, `ai_generation_outputs`, `billing_events`, and others enforce fixed UAC via `IMMUTABLE_UAC_CHECK` in `constraints.py`.

## Column conventions

- **UUID** — `UUID(as_uuid=True)` dialect column; application-generated via `uuid4` default on PK mixin
- **CITEXT** — case-insensitive text for slugs, codes, emails
- **JSONB** — flexible metadata with `'{}'::jsonb` or `'[]'::jsonb` server defaults
- **tsvector** — `content_assets.search_document` with GIN index for full-text search
- **Reserved names** — Python `metadata` columns mapped as `metadata_` with explicit column name `"metadata"`

## Model responsibilities

Each model provides:

- Typed `Mapped[]` columns
- Module and class docstrings
- PostgreSQL table `comment`
- `__repr__` safe for logs (no secrets)
- Named indexes and constraints matching `INDEX_STRATEGY.md`
- `relationship()` with `back_populates` on both sides

Models must **not** contain business logic, validation beyond CHECK constraints, or service-layer behavior.

## Import surface

`models/__init__.py` imports every model class and exposes them in `__all__`. Alembic and tests should import this module to register full metadata:

```python
import cloud_content_hub.infrastructure.database.models  # noqa: F401
```

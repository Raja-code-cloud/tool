# Relationships

Relationship wiring follows the approved ERD (`ERD.md`) and enforces tenant-safe composite foreign keys for workspace-scoped associations.

## Loading strategy

| Pattern                   | `lazy`                | Used for                                                                          |
| ------------------------- | --------------------- | --------------------------------------------------------------------------------- |
| Default ORM navigation    | `raise`               | All production relationships — forces explicit eager/load options in repositories |
| Catalog parent → children | `selectin` / `joined` | `AIProvider.models`, `AIModel.provider` (read-heavy catalog lookups)              |

## Tenancy relationship rules

### Organization → Workspace

```
Organization 1──* Workspace
Organization 1──* OrganizationMembership
Organization 1──* Subscription / BillingCustomer / QuotaPolicy
```

### Workspace aggregate root

`Workspace` is the inverse hub for all operational data: content, social, publishing, notifications, analytics, settings, and reliability tables scoped by `workspace_id`.

### Composite FK pattern

Child rows reference parents with matching tenant key:

```python
ForeignKeyConstraint(
    ["workspace_id", "asset_id"],
    ["content_assets.workspace_id", "content_assets.id"],
    ondelete="RESTRICT",
)
```

Used on: `articles`, `comments`, `publication_targets`, `metric_observations`, `collection_items`, and most workspace children.

### Cascade behavior

| Rule                 | Example                                                                    |
| -------------------- | -------------------------------------------------------------------------- |
| `RESTRICT` (default) | Business aggregates: assets, accounts, publications                        |
| `CASCADE`            | Junction hard-delete: `asset_tags`, `collection_items`, `role_permissions` |
| `SET NULL`           | Actor FKs: `created_by`, `updated_by`, `actor_id`, `author_id`             |

## Core content graph

```
ContentAsset 1──1 Article|Video|Poster|Thumbnail
ContentAsset 1──* ContentVersion (immutable)
ContentAsset 1──0..1 ContentDraft
ContentAsset *──* Tag (via asset_tags)
ContentAsset *──* Category (via asset_categories)
ContentAsset 1──* Comment
ContentAsset 1──* ApprovalRequest
ContentVersion 1──* Publication (via content_version relationship)
```

**Note:** The ORM relationship to `ContentVersion` is named `content_version` (not `version`) to avoid clashing with `VersionMixin.version`.

## AI flow

```
AIProvider 1──* AIModel
AIModel 1──* AIGenerationRequest
AIGenerationRequest 1──* AIGenerationOutput
AIGenerationRequest 1──* AIUsageRecord
ContentVersion ←── AIGenerationRequest (source_version)
BrandProfile ←── AIGenerationRequest
```

## Social & publishing flow

```
SocialPlatform 1──* SocialAccount
SocialAccount 1──0..1 OAuthTokenVault
SocialAccount 1──* PublicationTarget
Publication 1──* PublicationTarget
PublicationTarget 1──* PublicationSchedule
PublicationSchedule 1──* PublishingJob
PublishingJob 1──* PublishingAttempt
PublishingJob 0..1 JobLease
```

## Identity & RBAC

```
User 1──* ExternalIdentity
User 1──* OrganizationMembership
User 1──* WorkspaceMembership
WorkspaceMembership *──* Role (via membership_roles)
Role *──* Permission (via role_permissions)
```

System roles (`roles.is_system = true`) have `workspace_id IS NULL`. Custom roles are workspace-scoped.

## Analytics & usage

```
MetricDefinition 1──* MetricObservation
SocialAccount / PublicationTarget / ContentAsset ← optional MetricObservation FKs
UsageDimension 1──* UsageEvent
UsageDimension 1──* QuotaPolicy / QuotaPeriod
```

## Eventing & reliability

```
OutboxEvent ──logical──► InboxMessage (cross-service dedupe)
PublishingJob / BackgroundJob ──► DeadLetter (terminal failures)
Notification 1──* NotificationDelivery
```

## Circular import avoidance

Models use `from __future__ import annotations` and `TYPE_CHECKING` blocks for relationship type hints. String relationship targets (`"ContentAsset"`) defer resolution to mapper configuration time.

## Ambiguous FK disambiguation

When a model has multiple FKs to the same target (e.g., `User` for `created_by` and `user_id`), relationships specify `foreign_keys=[...]` explicitly.

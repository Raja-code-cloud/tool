# Backup Strategy

Cloud Content Hub AI relies on Azure platform-managed backups for durable state. Ephemeral runtime state is rebuilt from retries, outbox replay, and idempotent workers.

## Backup inventory

| Asset                   | Mechanism                           | Frequency                      | Retention                        | Owner       |
| ----------------------- | ----------------------------------- | ------------------------------ | -------------------------------- | ----------- |
| PostgreSQL (primary)    | Azure automated backup + PITR       | Continuous WAL, daily snapshot | 7–35 days (env-specific)         | Platform    |
| PostgreSQL (DR replica) | Geo-redundant backup / read replica | Continuous                     | Matches primary policy           | Platform    |
| Blob storage            | GRS / RA-GRS replication            | Continuous                     | 30-day soft delete (recommended) | Platform    |
| Redis                   | RDB snapshots (optional)            | Hourly (if enabled)            | 1–7 days                         | Platform    |
| Key Vault secrets       | Soft delete + purge protection      | On change                      | 90-day soft delete               | Security    |
| Container images        | ACR immutable tags                  | On CI build                    | 90+ days / lifecycle policy      | DevOps      |
| IaC (Bicep)             | Git repository                      | On merge                       | Indefinite                       | Engineering |
| Log Analytics           | Workspace retention                 | Continuous ingest              | 30–90 days                       | Platform    |

## PostgreSQL

Azure Database for PostgreSQL Flexible Server provides:

- **Automated backups** stored in geo-redundant storage when enabled.
- **Point-in-time recovery (PITR)** to any second within the retention window.
- **Geo-restore** to a paired region when geo-redundant backup is enabled.

Application data in scope:

- All 86 schema tables including `outbox_events`, `dead_letters`, tenant data, and audit logs.
- Alembic revision history (`alembic_version`).

Backup verification:

1. Quarterly restore to an isolated server in QA or DR.
2. Run `alembic current` and confirm head revision.
3. Execute `pytest tests/disaster_recovery -m integration` against the restored instance.
4. Record restore duration and data freshness (RPO achieved).

## Blob storage

Production storage accounts should use **Geo-Redundant Storage (GRS)** or **Geo-Zone-Redundant Storage (GZRS)**.

Logical containers (see `docs/backend/storage/CONTAINER_STRATEGY.md`):

- `posters`, `articles`, `videos`, `thumbnails`, `generated-content`, `temp`, `exports`, `logs`

Recommended platform settings:

- Soft delete enabled (blobs and containers).
- Versioning enabled for `exports` and user-generated content containers.
- Immutable storage policies for compliance archives where required.

Blob metadata in PostgreSQL (`content_assets`, file references) must be restored **with** the database; cross-referencing blob paths after DB restore validates consistency.

## Redis

Redis holds Celery broker state, result backends (if configured), and ephemeral cache entries.

| Data class              | Backup required | Recovery approach                     |
| ----------------------- | --------------- | ------------------------------------- |
| Celery task queue       | No              | Tasks retry from outbox / user action |
| Rate-limit counters     | No              | Reset on cold start                   |
| Session cache (if used) | No              | Users re-authenticate                 |
| Distributed locks       | No              | TTL expiry releases locks             |

Enable Azure Cache for Redis **premium persistence** only when operational review requires shorter RPO for in-flight tasks. Default policy accepts loss of queued-but-unprocessed Celery messages; outbox guarantees at-least-once redelivery.

## Configuration and secrets

| Item                          | Backup source                | Notes                                   |
| ----------------------------- | ---------------------------- | --------------------------------------- |
| `CCH_*` environment variables | Bicep parameters + Key Vault | No secrets in Git                       |
| Key Vault secret versions     | Azure native                 | Enable soft delete and purge protection |
| ACA revision history          | Azure platform               | Prior revisions retained for rollback   |
| Feature flags                 | PostgreSQL `settings`        | Included in DB backup                   |

Key Vault secrets (per environment):

- `CCH-DATABASE-URL`
- `CCH-MIGRATION-DATABASE-URL`
- `CCH-REDIS-URL`

Secrets rotation does not require image rebuild. Containers resolve Key Vault secret references at startup and on revision activation.

## Container images

Images are built once in CI and promoted by immutable tag (Git SHA):

| Image                      | Registry tag pattern |
| -------------------------- | -------------------- |
| `cloud-content-hub-api`    | `<env>-<git-sha>`    |
| `cloud-content-hub-worker` | `<env>-<git-sha>`    |

ACR retention policies prevent unbounded growth. Production DR (`dr.bicepparam`) pulls from the production registry (`acrcchprod.azurecr.io`).

## Automated backup verification

CI validates backup-related contracts without live Azure access:

```bash
pytest tests/backup -m backup
```

Checks include:

- Required DR documentation files exist and reference expected dependencies.
- Retention policy constants align with documented RPO/RTO targets.
- Restore checklist covers database, blob, Redis, secrets, and containers.

## Retention policy summary

| Environment | PostgreSQL PITR   | Blob soft delete | Log retention |
| ----------- | ----------------- | ---------------- | ------------- |
| dev         | 7 days            | 7 days           | 30 days       |
| qa          | 14 days           | 14 days          | 30 days       |
| prod        | 35 days           | 30 days          | 90 days       |
| dr          | 35 days (replica) | 30 days          | 90 days       |

Adjust values in Azure portal / IaC parameters to match organizational compliance requirements.

## Out of scope

- Frontend assets and CDN configuration (separate product team).
- Third-party OAuth provider configuration (restore from provider consoles).
- AI provider API keys (rotate via Key Vault; no historical backup required).

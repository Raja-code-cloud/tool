# Container Strategy

## Logical containers

Each container is a private partition for a content category. Default configured containers:

| Container           | Purpose                             |
| ------------------- | ----------------------------------- |
| `posters`           | Marketing and social poster images  |
| `articles`          | Article body assets and attachments |
| `videos`            | Video source and processed files    |
| `thumbnails`        | Derived preview images              |
| `generated-content` | AI-generated media and drafts       |
| `temp`              | Short-lived upload staging          |
| `exports`           | User-requested data exports         |
| `logs`              | Operational log archives            |

Containers are declared in `AzureStorageConfig.containers`. The provider rejects operations against unconfigured container names.

## BlobType mapping

`BlobType` enum values align with container names for deterministic routing:

```python
BlobType.POSTER          → "posters"
BlobType.ARTICLE         → "articles"
BlobType.VIDEO           → "videos"
BlobType.THUMBNAIL       → "thumbnails"
BlobType.GENERATED_CONTENT → "generated-content"
BlobType.TEMP            → "temp"
BlobType.EXPORT          → "exports"
BlobType.LOG             → "logs"
```

Application code selects the container when constructing `StorageLocation`.

## Provisioning

- **Production:** Provision private containers through deployment infrastructure (Terraform, Bicep, or Azure Portal). Set `auto_create_containers=False`.
- **Local/test:** Enable `auto_create_containers=True` for idempotent bootstrap via `ensure_private_containers`.

Auto-creation creates containers with default private access. It does not configure lifecycle policies, immutability, or CDN endpoints.

## Naming rules

Container names must match Azure constraints:

- Lowercase letters, digits, and hyphens only
- 3–63 characters
- Start and end with a letter or digit
- No consecutive hyphens

Validated by `validate_container_name` in `azure/containers.py`.

## Security

- All containers must remain private. The health check fails if any configured container has public access enabled.
- Cross-container copy is supported when both containers are configured.
- Tenant isolation is enforced at the blob path prefix level, not by per-tenant containers.

## Future providers

The same logical container names apply across providers. Adapter-specific naming normalization belongs in each provider implementation.

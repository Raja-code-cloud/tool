# Storage Architecture

## Purpose

The storage infrastructure provides a provider-neutral object storage layer for Cloud Content Hub AI. Application and worker code depend on the `StorageProvider` protocol; Azure Blob Storage is the default adapter.

Canonical implementation path:

```text
backend/src/cloud_content_hub/infrastructure/storage/
```

## Design principles

- **Port and adapter:** Business code never imports Azure SDK types.
- **Async-first:** All I/O-bound operations are asynchronous.
- **Dependency injection:** Providers are constructed in the composition root with typed configuration.
- **No global state:** Clients and credentials are owned by the provider instance.
- **Deterministic keys:** Blob names follow a tenant-scoped, date-partitioned layout.
- **Least privilege:** SAS URLs are short-lived and permission-scoped; credentials are never logged.

## Layering

```text
application ports (StorageProvider)
        │
        ▼
infrastructure/storage/
├── interfaces/storage_provider.py   ← Protocol
├── models.py                        ← Value objects
├── config.py                        ← Typed settings
├── exceptions.py                    ← Stable failure vocabulary
├── utils.py                         ← Naming and metadata helpers
├── validators/                      ← Trust-boundary checks
├── azure/                           ← Azure Blob adapter
└── testing/                         ← Fakes and fixtures
```

Future providers (AWS S3, Google Cloud Storage, local filesystem) implement the same protocol without changing application code.

## Core operations

| Operation                       | Description                                                                       |
| ------------------------------- | --------------------------------------------------------------------------------- |
| `upload`                        | Streaming or buffered upload with validation, metadata, tags, and ETag conditions |
| `download`                      | Async byte stream with optional range and ETag conditions                         |
| `delete`                        | Blob removal with optional optimistic concurrency                                 |
| `exists`                        | Existence probe                                                                   |
| `copy`                          | Server-side copy within the provider                                              |
| `move`                          | Copy followed by delete (non-atomic)                                              |
| `list`                          | Prefix listing with pagination                                                    |
| `generate_sas_url`              | Time-limited delegated access URL                                                 |
| `get_metadata` / `set_metadata` | Blob property access and mutation                                                 |
| `get_url`                       | Canonical HTTPS URL (not a credential)                                            |
| `health_check`                  | Connectivity and container accessibility probe                                    |
| `close`                         | Release client and credential resources                                           |

## Security

- HTTPS-only account and public base URLs.
- Managed Identity preferred in production; connection strings for controlled local use.
- Private containers; health check fails if public access is detected.
- Encryption at rest is provided by Azure; the adapter does not disable it.
- Structured logs record operation, container, blob name, size, and duration — never secrets or signed URLs.

## Retry and resilience

Azure SDK `RetryPolicy` with exponential backoff handles transient failures at the transport layer. A `circuit_breaker_hook` callback records operation outcomes for future circuit-breaker integration without selecting a library.

## Related documents

- [Azure Provider](AZURE_PROVIDER.md)
- [Container Strategy](CONTAINER_STRATEGY.md)
- [Upload Flow](UPLOAD_FLOW.md)
- [Download Flow](DOWNLOAD_FLOW.md)
- [SAS URL Guide](SAS_URL_GUIDE.md)
- [File Naming](FILE_NAMING.md)
- [Validation Rules](VALIDATION_RULES.md)
- [Health Checks](HEALTH_CHECKS.md)
- [Configuration](CONFIGURATION.md)
- [Testing](TESTING.md)

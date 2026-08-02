# Storage infrastructure

The canonical implementation is
`backend/src/cloud_content_hub/infrastructure/storage`. Application code depends on the
`StorageProvider` protocol, not Azure SDK types. The Azure adapter and deterministic in-memory
provider implement upload, streaming/ranged download, delete, existence checks, copy, move,
listing, SAS generation, metadata mutation, URLs, and health checks.

## Design

- Blob names are deterministic:
  `{tenant}/{user}/{yyyy}/{mm}/{dd}/{type}/{uuid}/{filename}`.
- Containers are private logical partitions and must be explicitly configured.
- Uploads validate path, MIME type, size, metadata, and optional SHA-256.
- ETags provide optimistic conditions for upload, download, metadata updates, and delete.
- SAS URLs use user-delegation keys, HTTPS, an explicit permission set, and a maximum 24-hour TTL.
- The adapter logs only provider, operation, and outcome. It never logs credentials or signed URLs.
- A callback hook records circuit-breaker outcomes without selecting a circuit-breaker library.

## Documentation

| Document                                           | Topic                       |
| -------------------------------------------------- | --------------------------- |
| [STORAGE_ARCHITECTURE.md](STORAGE_ARCHITECTURE.md) | Overall design and layering |
| [AZURE_PROVIDER.md](AZURE_PROVIDER.md)             | Azure adapter details       |
| [CONTAINER_STRATEGY.md](CONTAINER_STRATEGY.md)     | Logical container layout    |
| [UPLOAD_FLOW.md](UPLOAD_FLOW.md)                   | Upload pipeline             |
| [DOWNLOAD_FLOW.md](DOWNLOAD_FLOW.md)               | Download and range requests |
| [SAS_URL_GUIDE.md](SAS_URL_GUIDE.md)               | Delegated access tokens     |
| [FILE_NAMING.md](FILE_NAMING.md)                   | Deterministic blob paths    |
| [VALIDATION_RULES.md](VALIDATION_RULES.md)         | Trust-boundary validators   |
| [HEALTH_CHECKS.md](HEALTH_CHECKS.md)               | Connectivity probes         |
| [CONFIGURATION.md](CONFIGURATION.md)               | Typed settings              |
| [OPERATIONS.md](OPERATIONS.md)                     | Runtime behavior            |
| [TESTING.md](TESTING.md)                           | Fakes, mocks, and contracts |

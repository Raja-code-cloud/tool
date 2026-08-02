# Storage configuration

Construct `AzureStorageConfig` once in the composition root and inject it into
`AzureBlobStorageProvider`. It is frozen and validates HTTPS, credential exclusivity, retry
bounds, chunk sizes, maximum size, and container uniqueness.

## Key settings

| Field                                                   | Description                                                     |
| ------------------------------------------------------- | --------------------------------------------------------------- |
| `account_url`                                           | HTTPS Azure storage account URL                                 |
| `public_base_url`                                       | Optional CDN or custom domain for `get_url()`                   |
| `credential_mode`                                       | `managed_identity`, `service_principal`, or `connection_string` |
| `containers`                                            | Tuple of allowed private container names                        |
| `auto_create_containers`                                | Idempotent local bootstrap (default `False`)                    |
| `max_size_bytes`                                        | Maximum upload size                                             |
| `upload_chunk_size_bytes` / `download_chunk_size_bytes` | Transfer chunk sizes                                            |
| `timeout_seconds`                                       | Connection and read timeouts                                    |
| `retry_total` / `retry_backoff_seconds`                 | Exponential retry policy                                        |

Credential modes:

- `managed_identity`: preferred; optionally select a user-assigned identity by client ID.
- `service_principal`: requires tenant ID, client ID, and client secret.
- `connection_string`: intended for controlled local/test environments.

Never log or serialize the configuration object. Secret fields have redacted representations.
Production should leave container auto-creation disabled and provision private containers through
deployment infrastructure. Auto-creation is suitable for local bootstrap and is idempotent.

The `.env.example` values document deployment names; wiring these values into the application-wide
settings/composition root is intentionally outside this infrastructure-only implementation.

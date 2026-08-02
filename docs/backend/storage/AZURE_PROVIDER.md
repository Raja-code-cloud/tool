# Azure Blob Storage Provider

## Overview

`AzureBlobStorageProvider` implements the `StorageProvider` protocol using the Azure Blob Storage async SDK and Azure Identity.

## Components

| Module                  | Responsibility                                                       |
| ----------------------- | -------------------------------------------------------------------- |
| `azure/client.py`       | Constructs `BlobServiceClient` with credential mode and retry policy |
| `azure/provider.py`     | Port implementation: upload, download, list, SAS, health             |
| `azure/blob_service.py` | SDK response translation and error mapping                           |
| `azure/containers.py`   | Container name validation and optional auto-creation                 |
| `azure/sas.py`          | User-delegation SAS generation                                       |
| `azure/streaming.py`    | Upload stream validation, checksum, progress                         |

## Authentication modes

Configure via `AzureStorageConfig.credential_mode`:

| Mode                | Use case                                                                                |
| ------------------- | --------------------------------------------------------------------------------------- |
| `managed_identity`  | Production (default). Optional user-assigned identity via `managed_identity_client_id`. |
| `service_principal` | CI/CD or cross-tenant automation. Requires tenant, client ID, and secret.               |
| `connection_string` | Local development and Azurite. Mutually exclusive with other credential fields.         |

## Client lifecycle

1. Construct `AzureStorageConfig` in the composition root.
2. Instantiate `AzureBlobStorageProvider(config)`.
3. Call `await provider.initialize()` when `auto_create_containers` is enabled.
4. Inject the provider into application services through the port.
5. Call `await provider.close()` during application shutdown.

## SDK features used

- `BlobServiceClient`, `ContainerClient`, `BlobClient`
- Streaming upload via async iterables
- Streaming download via `StorageStreamDownloader.chunks()`
- Server-side synchronous copy (`start_copy_from_url`)
- User-delegation SAS with HTTPS-only protocol
- ETag-based optimistic concurrency (`MatchConditions.IfNotModified`)
- Blob metadata, tags, and content settings (type, encoding, disposition, cache control)

## Error translation

Azure SDK exceptions are mapped to provider-neutral types:

| Azure exception               | Storage exception                                              |
| ----------------------------- | -------------------------------------------------------------- |
| `ResourceNotFoundError`       | `BlobNotFoundError` or `ContainerNotFoundError`                |
| `ResourceExistsError`         | `BlobAlreadyExistsError`                                       |
| `ResourceModifiedError`       | `StorageConditionError`                                        |
| `ClientAuthenticationError`   | `StorageAuthenticationError`                                   |
| Transient HTTP/service errors | `UploadFailed`, `DownloadFailed`, or `StorageUnavailableError` |

## Retry policy

`RetryPolicy` with `RetryMode.Exponential` is configured from `retry_total` and `retry_backoff_seconds` in `AzureStorageConfig`. Connection and read timeouts come from `timeout_seconds`.

## Circuit breaker hook

Pass an optional async callback `(operation: str, success: bool) -> None` to record outcomes. The hook is invoked after each logged operation and is intended as a placeholder for external circuit-breaker libraries.

## Operational notes

- Copy is server-side and synchronous; move is copy + delete and is not atomic.
- SAS generation requires account-level permission to obtain a user delegation key.
- Do not log connection strings, client secrets, or generated SAS tokens.

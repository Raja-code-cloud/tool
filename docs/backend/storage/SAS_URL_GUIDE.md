# SAS URL Guide

## Purpose

Shared Access Signatures (SAS) provide time-limited, least-privilege access to individual blobs without exposing account credentials.

## Generation

```python
url = await provider.generate_sas_url(
    location,
    [SasPermission.READ],
    expires_in=timedelta(minutes=15),
)
```

## Permission model

| Permission             | Grants                           |
| ---------------------- | -------------------------------- |
| `SasPermission.READ`   | Read blob content and properties |
| `SasPermission.WRITE`  | Write/create blob content        |
| `SasPermission.DELETE` | Delete the blob                  |

Request only the permissions required for the operation. Prefer read-only tokens for download links.

## Expiration

- Must be positive and at most 24 hours.
- Use the shortest practical TTL for the use case.
- Expiry is enforced at generation time; invalid values raise `StorageValidationError`.

## Azure implementation

The adapter uses **user delegation SAS**:

1. Obtains a user delegation key from the storage account.
2. Generates a blob SAS with HTTPS-only protocol.
3. Appends the token to the blob URL returned by `get_url`.

Requires the executing identity to have permission to obtain delegation keys (typically `Storage Blob Data Contributor` or equivalent).

## Security rules

- **Never log** generated SAS URLs or delegation keys.
- **Never persist** SAS URLs in the database as permanent access paths.
- **Never expose** SAS URLs through public API responses without explicit business need and short TTL.
- Prefer issuing SAS from the application layer after authorization, not from untrusted clients.

## Failure handling

SAS generation failures raise `SASGenerationFailedError`. Common causes:

- Insufficient identity permissions
- Invalid account name
- Clock skew beyond the delegation key window

## Comparison with `get_url`

`get_url()` returns the canonical HTTPS blob URL **without** credentials. Access requires account-level authentication or a separately issued SAS. Do not treat bare URLs as publicly accessible.

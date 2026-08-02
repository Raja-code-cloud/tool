# Download Flow

## Request model

Downloads use a `DownloadRequest`:

```python
DownloadRequest(
    location=StorageLocation(container="videos", blob_name="..."),
    offset=0,           # optional byte offset
    length=4096,        # optional byte length (range request)
    expected_etag='"..."',  # optional optimistic concurrency
    progress=callback,    # optional async (transferred, total)
)
```

## Return type

`download()` returns an `AsyncIterator[bytes]`. Consumers must iterate within the request or job lifetime and propagate cancellation.

## Processing steps

1. **Location validation** — Container and blob name checks.
2. **Blob fetch** — `BlobClient.download_blob` with optional offset, length, and ETag condition.
3. **Stream iteration** — Chunks yielded through `iter_download` with optional progress reporting.
4. **Logging** — Success logged after the stream completes; failures logged immediately.

## Range requests

Set `offset` and optionally `length` for partial content retrieval. This maps directly to Azure range headers. Useful for resumable downloads and media seeking.

## ETag support

Provide `expected_etag` to ensure the blob has not changed since metadata was read. Mismatch raises `StorageConditionError`.

## Metadata retrieval

Use `get_metadata(location)` separately to obtain size, content type, ETag, tags, and custom metadata without downloading content.

## Blob properties

`BlobMetadata` returned by `get_metadata` and successful uploads includes:

- `size`, `content_type`, `etag`, `last_modified`
- `metadata`, `tags`
- `checksum_sha256` (from blob metadata when present)
- `content_disposition`, `content_encoding`, `cache_control`

## Error outcomes

| Condition      | Exception               |
| -------------- | ----------------------- |
| Blob not found | `BlobNotFoundError`     |
| ETag mismatch  | `StorageConditionError` |
| Azure failure  | `DownloadFailed`        |

## Operational guidance

- Apply timeouts at the HTTP/job layer; the storage adapter uses SDK read timeouts from configuration.
- Do not buffer entire large objects in memory; consume the async iterator incrementally.
- Do not log downloaded content or signed URLs.

# Upload Flow

## Request model

Uploads are expressed as an `UploadRequest` value object:

```python
UploadRequest(
    location=StorageLocation(container="articles", blob_name="..."),
    data=bytes | AsyncIterable[bytes],
    content_type="image/png",
    content_length=1024,          # recommended for streams
    metadata={"workspace_id": "..."},
    tags={"source": "upload-wizard"},
    checksum_sha256="...",        # optional integrity check
    overwrite=False,
    expected_etag='"..."',        # optional optimistic concurrency
    progress=callback,            # optional async (transferred, total)
)
```

## Processing steps

1. **Location validation** — Container must be configured; blob name must pass path traversal checks.
2. **MIME validation** — Content type is normalized and checked against allowed prefixes.
3. **Size validation** — `content_length` and actual byte count must not exceed `max_size_bytes`; empty files are rejected.
4. **Checksum** — Optional SHA-256 is validated on format; computed for byte uploads; verified after stream completion.
5. **Metadata sanitization** — Keys and values are validated; checksum is stored in blob metadata.
6. **Stream wrapping** — Async streams pass through `validated_upload_stream` for size, checksum, and progress.
7. **Azure upload** — `BlobClient.upload_blob` with content settings, tags, and optional ETag condition.
8. **Logging** — Structured `storage.operation` event with duration, size, and outcome.

## Overwrite protection

Set `overwrite=False` (default). Azure raises `ResourceExistsError`, translated to `BlobAlreadyExistsError`.

## Optimistic concurrency

Provide `expected_etag` from a prior read. Upload fails with `StorageConditionError` if the blob was modified.

## Streaming uploads

For large files, pass an `AsyncIterable[bytes]` as `data`:

- Always supply `content_length` when known.
- Chunks are validated incrementally; exceeding `max_size_bytes` raises `FileTooLargeError`.
- Progress callback receives `(bytes_transferred, total_or_none)`.

## Content settings

The adapter sets:

- `content_type` — validated MIME
- `content_disposition` — optional
- `content_encoding` — optional
- `cache_control` — optional

## Filename sanitization

Use `build_blob_name()` in `utils.py` to produce a deterministic, collision-resistant path before constructing `StorageLocation`. See [File Naming](FILE_NAMING.md).

## Error outcomes

| Condition         | Exception                |
| ----------------- | ------------------------ |
| MIME not allowed  | `InvalidMimeTypeError`   |
| Size exceeded     | `FileTooLargeError`      |
| Empty content     | `StorageValidationError` |
| Checksum mismatch | `ChecksumMismatchError`  |
| Blob exists       | `BlobAlreadyExistsError` |
| ETag mismatch     | `StorageConditionError`  |
| Azure failure     | `UploadFailed`           |

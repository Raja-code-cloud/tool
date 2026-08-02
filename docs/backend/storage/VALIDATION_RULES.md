# Validation Rules

## Overview

Validators in `infrastructure/storage/validators/` enforce trust-boundary checks before data reaches a storage provider. They raise typed exceptions from `exceptions.py`.

## MIME type (`validators/mime.py`)

- Normalizes content type (strips parameters, lowercases).
- Rejects control characters and empty values.
- Default allowlist prefixes: `application/`, `audio/`, `image/`, `text/`, `video/`.
- Custom allowlists can be passed to `validate_mime_type()`.
- Raises `InvalidMimeTypeError`.

## File size (`validators/size.py`)

- Rejects negative sizes.
- Enforces `max_size_bytes` from configuration.
- Rejects zero-byte uploads via `validate_not_empty()`.
- Raises `FileTooLargeError` or `StorageValidationError`.

## Filename (`validators/filename.py`)

- `validate_filename()` — base name only; blocks path segments and unsafe characters.
- `validate_blob_name()` — full object key; blocks traversal and unsafe segments.
- Raises `StorageValidationError`.

## Extension whitelist (`validators/extension.py`)

- `validate_extension(filename, allowed_extensions)` — ensures the file suffix is in an explicit allowlist.
- Raises `StorageValidationError`.

## Checksum (`validators/checksum.py`)

- `validate_checksum()` — format check for 64-char lowercase hex SHA-256.
- `sha256_hex(data)` — compute digest.
- `verify_checksum(data, expected)` — constant-time comparison.
- Raises `ChecksumMismatchError` on mismatch.

## Metadata (`utils.sanitize_metadata`)

- Keys must match `[A-Za-z_][A-Za-z0-9_]{0,127}`.
- Values max 2048 chars; no line breaks.
- Raises `StorageValidationError`.

## Container names (`azure/containers.py`)

- Azure naming rules: lowercase, 3–63 chars, no consecutive hyphens.
- Must appear in `AzureStorageConfig.containers`.
- Raises `StorageValidationError` or `ContainerNotFoundError` at runtime.

## Validation order on upload

1. Location (container + blob name)
2. MIME type
3. Size and empty-file check
4. Checksum format (if provided)
5. Stream validation (size + checksum during transfer)
6. Metadata sanitization

## Application-layer validation

Business rules (workspace quotas, content policy, malware scan state) belong in application services, not this infrastructure layer. Infrastructure validators cover transport and storage safety only.

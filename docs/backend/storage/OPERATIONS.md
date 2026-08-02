# Storage operations

Uploads accept bytes or an async byte stream. Supply `content_length` when known, a SHA-256 digest
when integrity must be verified, and an async progress callback for transfer reporting. Set
`overwrite` explicitly and use `expected_etag` for optimistic concurrency.

Downloads are async iterators and support byte `offset` and `length`. Consumers must iterate the
stream within the request lifetime and propagate cancellation.

SAS generation requires an explicit subset of read, write, and delete permissions. Prefer read-only
tokens, use the shortest practical expiry, and never log or persist the resulting URL.

Health checks call account information only. They do not enumerate or mutate tenant blobs and return
a safe `reachable` or `unavailable` detail. Close the provider during application shutdown to release
the Azure credential and HTTP transport.

Copy uses Azure server-side synchronous copy. Move is copy followed by delete and is therefore not
atomic; callers requiring workflow atomicity must track that state outside this infrastructure layer.

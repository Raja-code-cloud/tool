# Storage testing

`InMemoryStorageProvider` is a deterministic, network-free implementation of the owned port. It
supports lifecycle, range, pagination, ETag, metadata, SAS-shape, and health behavior. It stores
bytes only in process and performs no filesystem I/O.

`create_mock_storage_provider` provides an autospecced mock for tests that only need to assert
application orchestration. Synthetic sample request and location factories live in
`storage.testing.fixtures`.

The contract suite exercises the fake through the same public operations expected from any
provider. Azure SDK integration behavior should be tested separately against Azurite or an approved
sandbox and marked `integration`/`external`; those tests are intentionally not part of the
network-free unit suite.

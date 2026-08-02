"""Immutable Azure storage configuration."""

from dataclasses import dataclass, field
from enum import StrEnum

from cloud_content_hub.infrastructure.storage.exceptions import StorageValidationError

DEFAULT_CONTAINERS: tuple[str, ...] = (
    "posters",
    "articles",
    "videos",
    "thumbnails",
    "generated-content",
    "temp",
    "exports",
    "logs",
)


class AzureCredentialMode(StrEnum):
    CONNECTION_STRING = "connection_string"
    MANAGED_IDENTITY = "managed_identity"
    SERVICE_PRINCIPAL = "service_principal"


@dataclass(frozen=True, slots=True)
class AzureStorageConfig:
    account_url: str
    credential_mode: AzureCredentialMode = AzureCredentialMode.MANAGED_IDENTITY
    connection_string: str | None = field(default=None, repr=False)
    tenant_id: str | None = None
    client_id: str | None = None
    client_secret: str | None = field(default=None, repr=False)
    managed_identity_client_id: str | None = None
    containers: tuple[str, ...] = DEFAULT_CONTAINERS
    public_base_url: str | None = None
    auto_create_containers: bool = False
    max_size_bytes: int = 100 * 1024 * 1024
    upload_chunk_size_bytes: int = 4 * 1024 * 1024
    download_chunk_size_bytes: int = 4 * 1024 * 1024
    timeout_seconds: float = 30.0
    retry_total: int = 3
    retry_backoff_seconds: float = 0.8

    def __post_init__(self) -> None:
        if not self.account_url.startswith("https://"):
            raise StorageValidationError("Azure account URL must use HTTPS")
        if self.public_base_url is not None and not self.public_base_url.startswith("https://"):
            raise StorageValidationError("Public base URL must use HTTPS")
        if not self.containers or len(set(self.containers)) != len(self.containers):
            raise StorageValidationError("At least one unique container is required")
        if self.max_size_bytes <= 0 or self.upload_chunk_size_bytes <= 0:
            raise StorageValidationError("Storage size settings must be positive")
        if self.download_chunk_size_bytes <= 0 or self.timeout_seconds <= 0:
            raise StorageValidationError("Storage timeout and chunk size must be positive")
        if self.retry_total < 0 or self.retry_backoff_seconds < 0:
            raise StorageValidationError("Storage retry settings cannot be negative")
        self._validate_credentials()

    def _validate_credentials(self) -> None:
        if self.credential_mode is AzureCredentialMode.CONNECTION_STRING:
            if not self.connection_string:
                raise StorageValidationError("Connection string credential is missing")
            return
        if self.connection_string is not None:
            raise StorageValidationError("Connection string is only valid for its credential mode")
        if self.credential_mode is AzureCredentialMode.SERVICE_PRINCIPAL:
            if not all((self.tenant_id, self.client_id, self.client_secret)):
                raise StorageValidationError("Service principal credentials are incomplete")
            return
        if any((self.tenant_id, self.client_secret)):
            raise StorageValidationError("Service principal fields require service principal mode")

    @property
    def base_url(self) -> str:
        return (self.public_base_url or self.account_url).rstrip("/")

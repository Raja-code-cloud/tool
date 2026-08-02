"""Azure Blob async client construction and ownership."""

from azure.core.pipeline.policies import RetryMode, RetryPolicy
from azure.identity.aio import ClientSecretCredential, DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

from cloud_content_hub.infrastructure.storage.config import (
    AzureCredentialMode,
    AzureStorageConfig,
)


def create_blob_service_client(config: AzureStorageConfig) -> BlobServiceClient:
    retry_policy = RetryPolicy(
        retry_total=config.retry_total,
        retry_mode=RetryMode.Exponential,
        retry_backoff_factor=config.retry_backoff_seconds,
    )
    if config.credential_mode is AzureCredentialMode.CONNECTION_STRING:
        assert config.connection_string is not None
        return BlobServiceClient.from_connection_string(
            config.connection_string,
            retry_policy=retry_policy,
            connection_timeout=config.timeout_seconds,
            read_timeout=config.timeout_seconds,
        )
    credential: ClientSecretCredential | DefaultAzureCredential
    if config.credential_mode is AzureCredentialMode.SERVICE_PRINCIPAL:
        assert config.tenant_id and config.client_id and config.client_secret
        credential = ClientSecretCredential(
            tenant_id=config.tenant_id,
            client_id=config.client_id,
            client_secret=config.client_secret,
        )
    else:
        credential = DefaultAzureCredential(
            managed_identity_client_id=config.managed_identity_client_id,
        )
    return BlobServiceClient(
        account_url=config.account_url,
        credential=credential,
        retry_policy=retry_policy,
        connection_timeout=config.timeout_seconds,
        read_timeout=config.timeout_seconds,
    )

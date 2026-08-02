"""Least-privilege user-delegation SAS generation."""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from azure.storage.blob.aio import BlobServiceClient

from cloud_content_hub.infrastructure.storage.exceptions import SASGenerationFailedError
from cloud_content_hub.infrastructure.storage.models import SasPermission, StorageLocation


async def generate_user_delegation_sas(
    client: BlobServiceClient,
    account_name: str,
    location: StorageLocation,
    permissions: Sequence[SasPermission],
    expires_in: timedelta,
) -> str:
    now = datetime.now(UTC)
    expiry = now + expires_in
    try:
        delegation_key = await client.get_user_delegation_key(now - timedelta(minutes=5), expiry)
        requested = frozenset(permissions)
        return generate_blob_sas(
            account_name=account_name,
            container_name=location.container,
            blob_name=location.blob_name,
            user_delegation_key=delegation_key,
            permission=BlobSasPermissions(
                read=SasPermission.READ in requested,
                write=SasPermission.WRITE in requested,
                create=SasPermission.WRITE in requested,
                delete=SasPermission.DELETE in requested,
            ),
            start=now - timedelta(minutes=5),
            expiry=expiry,
            protocol="https",
        )
    except Exception as error:
        raise SASGenerationFailedError("User delegation SAS generation failed") from error

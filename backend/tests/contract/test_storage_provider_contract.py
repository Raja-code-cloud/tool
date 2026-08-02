from datetime import timedelta

import pytest

from cloud_content_hub.infrastructure.storage.exceptions import (
    BlobNotFoundError,
    StorageConditionError,
)
from cloud_content_hub.infrastructure.storage.models import DownloadRequest, SasPermission
from cloud_content_hub.infrastructure.storage.testing.fake import InMemoryStorageProvider
from cloud_content_hub.infrastructure.storage.testing.fixtures import (
    SAMPLE_BYTES,
    sample_location,
    sample_upload_request,
)

pytestmark = pytest.mark.contract


async def test_in_memory_provider_supports_complete_lifecycle() -> None:
    provider = InMemoryStorageProvider()
    source = sample_location()
    uploaded = await provider.upload(sample_upload_request())

    downloaded = b"".join([chunk async for chunk in provider.download(DownloadRequest(source))])
    assert downloaded == SAMPLE_BYTES
    assert await provider.exists(source)
    assert (await provider.get_metadata(source)).etag == uploaded.etag

    destination = type(source)(source.container, f"{source.blob_name}.copy")
    copied = await provider.copy(source, destination)
    assert copied.location == destination
    moved = type(source)(source.container, f"{source.blob_name}.moved")
    await provider.move(destination, moved)
    assert not await provider.exists(destination)

    page = await provider.list(source.container, prefix="tenant-a/", limit=1)
    assert len(page.items) == 1
    assert page.continuation_token == "1"

    sas = await provider.generate_sas_url(
        source,
        [SasPermission.READ],
        expires_in=timedelta(minutes=5),
    )
    assert "permissions=read" in sas
    assert (await provider.health_check()).healthy

    await provider.delete(source, expected_etag=uploaded.etag)
    with pytest.raises(BlobNotFoundError):
        await provider.get_metadata(source)


async def test_provider_enforces_etag_conditions() -> None:
    provider = InMemoryStorageProvider()
    location = sample_location()
    await provider.upload(sample_upload_request())

    with pytest.raises(StorageConditionError):
        await provider.delete(location, expected_etag='"wrong"')

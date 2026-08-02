"""Private logical Azure container lifecycle."""

import re

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob.aio import BlobServiceClient

from cloud_content_hub.infrastructure.storage.exceptions import StorageValidationError

_CONTAINER = re.compile(r"^[a-z0-9](?:[a-z0-9-]{1,61}[a-z0-9])$")


def validate_container_name(name: str) -> str:
    if not _CONTAINER.fullmatch(name) or "--" in name:
        raise StorageValidationError("Invalid Azure container name")
    return name


async def ensure_private_containers(
    client: BlobServiceClient,
    containers: tuple[str, ...],
) -> None:
    for container in containers:
        validate_container_name(container)
        try:
            await client.create_container(container)
        except ResourceExistsError:
            continue

"""Application-layer port definitions."""

from cloud_content_hub.application.shared.interfaces.ai_generation import (
    AIGenerationPort,
    ApplicationGenerationRequest,
    ApplicationGenerationResponse,
)
from cloud_content_hub.application.shared.interfaces.job_queue import (
    BackgroundJobRecord,
    IBackgroundJobRepository,
    JobQueueName,
    JobState,
)
from cloud_content_hub.application.shared.interfaces.object_storage import (
    BlobMetadataRecord,
    IObjectStoragePort,
    StorageLocationRecord,
    UploadPayload,
)
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork

__all__ = [
    "AIGenerationPort",
    "ApplicationGenerationRequest",
    "ApplicationGenerationResponse",
    "BackgroundJobRecord",
    "BlobMetadataRecord",
    "IBackgroundJobRepository",
    "IObjectStoragePort",
    "IUnitOfWork",
    "JobQueueName",
    "JobState",
    "StorageLocationRecord",
    "UploadPayload",
]

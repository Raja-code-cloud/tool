"""Publication business validation."""

from __future__ import annotations

from uuid import UUID

from cloud_content_hub.application.publishing.dto.requests import CreatePublicationRequestDto
from cloud_content_hub.application.publishing.exceptions.publishing_errors import (
    ApprovalRequiredError,
    PublicationValidationError,
    SocialAccountUnhealthyError,
)
from cloud_content_hub.application.publishing.interfaces.publication_repository import (
    PublicationRecord,
    PublicationStatus,
)
from cloud_content_hub.core.errors import StateTransitionError


def validate_create_publication(
    request: CreatePublicationRequestDto,
    *,
    asset_id: UUID,
    version_approved: bool,
    accounts_healthy: bool,
) -> None:
    """Validate publication creation business rules."""

    if not version_approved:
        raise ApprovalRequiredError(detail="Content version must be approved and immutable.")
    if not accounts_healthy:
        raise SocialAccountUnhealthyError()
    account_ids = {target.social_account_id for target in request.targets}
    if len(account_ids) != len(request.targets):
        raise PublicationValidationError(detail="Publication targets must be unique.")
    if asset_id is None:
        raise PublicationValidationError(detail="Content version must belong to a valid asset.")


def validate_dispatch(publication: PublicationRecord) -> None:
    """Validate that a publication can be dispatched."""

    if publication.status not in {PublicationStatus.DRAFT, PublicationStatus.READY}:
        raise PublicationValidationError(
            detail="Only draft or ready publications can be dispatched.",
            parameters={"status": publication.status.value},
        )


def validate_cancellation(publication: PublicationRecord) -> None:
    """Validate that a publication can be cancelled."""

    if publication.status in {PublicationStatus.COMPLETED, PublicationStatus.CANCELLED}:
        raise StateTransitionError(
            detail="Publication cannot be cancelled from its current state.",
            parameters={"status": publication.status.value},
        )

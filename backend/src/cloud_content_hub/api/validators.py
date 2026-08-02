from uuid import UUID

from cloud_content_hub.core.errors import ValidationError


def parse_uuid(value: str, *, field: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        raise ValidationError(detail=f"{field} must be a valid UUID.") from exc

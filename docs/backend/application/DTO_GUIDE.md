# DTO Guide

Application DTOs are Pydantic v2 models used for handler inputs and outputs. They align with the API contracts in `docs/backend/api/COMMON_SCHEMAS.md` but live in the application layer — not in FastAPI route schemas.

## Location

Request DTOs: `<feature>/dto/requests.py`
Response DTOs: `<feature>/dto/responses.py`
Shared primitives: `application/shared/dto/base.py`

## Base types

### `ApplicationDto`

Base model with camelCase JSON aliases via `alias_generator`. All application DTOs inherit from this or `ResourceBaseDto`.

### `ResourceBaseDto`

Resources with identity and optimistic concurrency:

```python
class ResourceBaseDto(ApplicationDto):
    id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
```

### `OperationDto`

Asynchronous operation projection for 202 responses:

```python
class OperationDto(ResourceBaseDto):
    type: OperationType       # upload | generation | publishing | adminJob
    status: OperationStatus   # queued | running | succeeded | failed | cancelled
    resource_type: str | None
    resource_id: UUID | None
    error_code: str | None
```

### `PagedResultDto[T]`

```python
class PagedResultDto(ApplicationDto, Generic[T]):
    items: tuple[T, ...]
    page: PageInfoDto  # next_cursor, has_more, limit
```

## Feature DTOs

| Feature       | Request DTOs                                                   | Response DTOs                             |
| ------------- | -------------------------------------------------------------- | ----------------------------------------- |
| Assets        | `UploadAssetRequestDto`, `ReplaceAssetRequestDto`              | `AssetDto`, `AssetMediaDto`               |
| Content       | `GenerationRequestDto`, `RegenerationRequestDto`               | `ContentDto`                              |
| Publishing    | `CreatePublicationRequestDto`, `DispatchPublicationRequestDto` | `PublicationDto`, `PublicationTargetDto`  |
| Scheduler     | `ScheduleRequestDto`                                           | `ScheduleDto`                             |
| Analytics     | `ImportAnalyticsRequestDto`                                    | `AnalyticsDashboardDto`, `MetricValueDto` |
| Notifications | `MarkNotificationReadRequestDto`                               | `NotificationDto`                         |

## Mapping rules

1. Handlers never return repository read models or ORM instances.
2. Mappers live in `<feature>/mappers/` and convert read models → response DTOs.
3. Request DTOs are mapped to domain/repository inputs inside handlers or validators.
4. Nested DTOs follow API schema nesting (e.g., `AssetDto.media: AssetMediaDto | None`).
5. Decimal analytics values are strings in DTOs per API contract.

## Validation split

| Layer                     | Validates                                                 |
| ------------------------- | --------------------------------------------------------- |
| Delivery (FastAPI)        | Transport shape, headers, content types, size limits      |
| Application validators    | Business rules: state transitions, ownership, quotas, DST |
| Infrastructure validators | MIME detection, malware scan, checksum verification       |

Application DTOs use Pydantic field constraints for basic shape (min length, UUID format, regex patterns). Business validation that requires repository context lives in `<feature>/validators/`.

## Example

```python
# Request DTO (application layer)
class UploadAssetRequestDto(ApplicationDto):
    asset_type: AssetTypeDto
    title: str = Field(min_length=1, max_length=300)
    file_data: bytes
    ...

# Handler maps to repository input
asset = await repository.create(
    NewAsset(
        workspace_id=actor.workspace_id,
        asset_type=asset_type,
        title=command.request.title,
        ...
    )
)

# Response DTO (application layer)
return map_upload_operation(job)  # → OperationDto
```

Presentation layer (FastAPI) maps application DTOs to HTTP response envelopes (`Success<T>`, `PagedResponse<T>`) without adding business logic.

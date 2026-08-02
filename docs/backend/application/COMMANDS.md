# Commands

Commands are immutable dataclasses representing write intent. They carry no behavior; handlers own orchestration logic.

## Shared conventions

- Commands include an `idempotency_key` when the API requires `Idempotency-Key`.
- Mutations that support optimistic concurrency include `expected_version`.
- Handlers receive `ActorContext` separately from the command.

## Assets

### `UploadAssetCommand`

```python
@dataclass(frozen=True, slots=True)
class UploadAssetCommand:
    request: UploadAssetRequestDto
    idempotency_key: str
```

### `ReplaceAssetCommand`

```python
@dataclass(frozen=True, slots=True)
class ReplaceAssetCommand:
    asset_id: UUID
    expected_version: int
    request: ReplaceAssetRequestDto
    idempotency_key: str
```

### `DeleteAssetCommand`

```python
@dataclass(frozen=True, slots=True)
class DeleteAssetCommand:
    asset_id: UUID
    expected_version: int
```

## Content

### `GenerateContentCommand`

```python
@dataclass(frozen=True, slots=True)
class GenerateContentCommand:
    request: GenerationRequestDto
    idempotency_key: str
```

### `RegenerateContentCommand`

```python
@dataclass(frozen=True, slots=True)
class RegenerateContentCommand:
    request: RegenerationRequestDto
    idempotency_key: str
```

## Publishing

### `PublishContentCommand`

Creates a publication without dispatching it.

```python
@dataclass(frozen=True, slots=True)
class PublishContentCommand:
    request: CreatePublicationRequestDto
    idempotency_key: str
```

### `DispatchPublicationCommand`

```python
@dataclass(frozen=True, slots=True)
class DispatchPublicationCommand:
    publication_id: UUID
    expected_version: int
    request: DispatchPublicationRequestDto
    idempotency_key: str
```

### `CancelPublicationCommand`

```python
@dataclass(frozen=True, slots=True)
class CancelPublicationCommand:
    publication_id: UUID
    expected_version: int
```

## Scheduler

### `SchedulePublicationCommand`

```python
@dataclass(frozen=True, slots=True)
class SchedulePublicationCommand:
    request: ScheduleRequestDto
    idempotency_key: str
```

### `CancelScheduleCommand`

```python
@dataclass(frozen=True, slots=True)
class CancelScheduleCommand:
    schedule_id: UUID
    expected_version: int
```

## Analytics

### `ImportAnalyticsCommand`

```python
@dataclass(frozen=True, slots=True)
class ImportAnalyticsCommand:
    request: ImportAnalyticsRequestDto
    idempotency_key: str
```

## Notifications

### `MarkNotificationReadCommand`

```python
@dataclass(frozen=True, slots=True)
class MarkNotificationReadCommand:
    notification_id: UUID
    expected_version: int
    request: MarkNotificationReadRequestDto
```

## Handler return types

| Command                       | Returns                 |
| ----------------------------- | ----------------------- |
| Upload / Replace asset        | `OperationDto`          |
| Delete asset                  | `None`                  |
| Generate / Regenerate content | `OperationDto`          |
| Create publication            | `PublicationDto`        |
| Dispatch publication          | `OperationDto`          |
| Cancel publication            | `PublicationDto`        |
| Schedule publication          | `ScheduleDto`           |
| Cancel schedule               | `ScheduleDto`           |
| Import analytics              | `ImportAnalyticsResult` |
| Mark notification read        | `NotificationDto`       |

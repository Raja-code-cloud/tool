"""V1 success response envelopes for the HTTP delivery layer."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from cloud_content_hub.application.shared.dto.base import PageInfoDto
from cloud_content_hub.core.context import request_id_var


def to_camel(value: str) -> str:
    first, *rest = value.split("_")
    return first + "".join(part.capitalize() for part in rest)


def dump_dto(value: object) -> object:
    """Serialize application or transport DTOs for response envelopes."""

    if isinstance(value, BaseModel):
        return value.model_dump(by_alias=True, mode="json")
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return model_dump(by_alias=True, mode="json")
    if isinstance(value, (list, tuple)):
        return [dump_dto(item) for item in value]
    return value


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class PageMeta(ApiModel):
    next_cursor: str | None = None
    has_more: bool = False
    limit: int = Field(ge=1, le=100)


class Meta(ApiModel):
    request_id: str | None = None
    page: PageMeta | None = None
    warnings: list[str] | None = None


class SuccessEnvelope[T](ApiModel):
    success: bool = True
    message: str
    data: T
    meta: Meta | None = None


# Backward-compatible aliases used by existing scaffolding.
ResponseMeta = Meta
PageInfo = PageMeta
ResponseEnvelope = SuccessEnvelope


class CollectionEnvelope[T](ApiModel):
    """Legacy collection envelope; prefer SuccessEnvelope with meta.page."""

    success: bool = True
    message: str
    data: list[T]
    meta: Meta | None = None


def _request_id() -> str | None:
    return request_id_var.get()


def page_meta(page: PageInfoDto) -> PageMeta:
    return PageMeta(
        next_cursor=page.next_cursor,
        has_more=page.has_more,
        limit=page.limit,
    )


def build_meta(*, page: PageInfoDto | None = None, warnings: list[str] | None = None) -> Meta:
    return Meta(
        request_id=_request_id(),
        page=page_meta(page) if page is not None else None,
        warnings=warnings,
    )


def success[T](
    *,
    data: T,
    message: str,
    page: PageInfoDto | None = None,
) -> SuccessEnvelope[object]:
    return SuccessEnvelope(data=dump_dto(data), message=message, meta=build_meta(page=page))


def paged_success[T](
    *,
    items: tuple[T, ...] | list[T],
    page: PageInfoDto,
    message: str,
) -> SuccessEnvelope[list[object]]:
    return SuccessEnvelope(
        data=[dump_dto(item) for item in items],
        message=message,
        meta=build_meta(page=page),
    )


def list_success[T](
    *,
    items: tuple[T, ...] | list[T],
    message: str,
) -> SuccessEnvelope[list[object]]:
    return SuccessEnvelope(
        data=[dump_dto(item) for item in items],
        message=message,
        meta=build_meta(),
    )


def etag_for_version(version: int) -> str:
    return f'"{version}"'


class ProbeDto(ApiModel):
    status: str

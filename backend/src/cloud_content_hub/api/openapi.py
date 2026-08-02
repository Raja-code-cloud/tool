"""OpenAPI 3.1 customization for the v1 delivery layer."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

SECURITY_SCHEMES: dict[str, Any] = {
    "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Workspace-scoped access token.",
    },
}

COMMON_HEADERS: dict[str, Any] = {
    "WorkspaceId": {
        "name": "X-Workspace-ID",
        "in": "header",
        "required": True,
        "schema": {"type": "string", "format": "uuid"},
        "description": "Active workspace scope for tenant-isolated operations.",
    },
    "IfMatch": {
        "name": "If-Match",
        "in": "header",
        "required": True,
        "schema": {"type": "string"},
        "description": 'Optimistic concurrency ETag, e.g. `"2"`.',
    },
    "IdempotencyKey": {
        "name": "Idempotency-Key",
        "in": "header",
        "required": True,
        "schema": {"type": "string", "minLength": 8, "maxLength": 128},
        "description": "Idempotency token for duplicate-prone POST operations.",
    },
}

PROBLEM_JSON = {"application/problem+json": {"schema": {"$ref": "#/components/schemas/Failure"}}}

PROBLEM_RESPONSES: dict[str, Any] = {
    "BadRequest": {"description": "Malformed request.", "content": PROBLEM_JSON},
    "Unauthenticated": {"description": "Authentication required.", "content": PROBLEM_JSON},
    "Forbidden": {"description": "Permission denied.", "content": PROBLEM_JSON},
    "NotFound": {"description": "Resource not found.", "content": PROBLEM_JSON},
    "Conflict": {"description": "State or version conflict.", "content": PROBLEM_JSON},
    "Unprocessable": {"description": "Validation failed.", "content": PROBLEM_JSON},
    "RateLimited": {"description": "Rate limit exceeded.", "content": PROBLEM_JSON},
    "Unavailable": {"description": "Dependency unavailable.", "content": PROBLEM_JSON},
    "InternalError": {"description": "Unexpected server error.", "content": PROBLEM_JSON},
}

COMPONENT_SCHEMAS: dict[str, Any] = {
    "Failure": {
        "type": "object",
        "additionalProperties": False,
        "required": ["success", "error"],
        "properties": {
            "success": {"type": "boolean", "const": False},
            "error": {"$ref": "#/components/schemas/ApiError"},
            "type": {"type": "string", "format": "uri"},
            "title": {"type": "string"},
            "status": {"type": "integer"},
            "detail": {"type": "string"},
            "requestId": {"type": "string"},
        },
    },
    "ApiError": {
        "type": "object",
        "additionalProperties": False,
        "required": ["code", "message", "details"],
        "properties": {
            "code": {"type": "string"},
            "message": {"type": "string"},
            "details": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/ErrorDetail"},
            },
        },
    },
    "ErrorDetail": {
        "type": "object",
        "additionalProperties": False,
        "required": ["code", "message"],
        "properties": {
            "field": {"type": "string"},
            "code": {"type": "string"},
            "message": {"type": "string"},
        },
    },
    "Meta": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "requestId": {"type": "string"},
            "page": {"$ref": "#/components/schemas/Page"},
            "warnings": {"type": "array", "items": {"type": "string"}},
        },
    },
    "Page": {
        "type": "object",
        "additionalProperties": False,
        "required": ["nextCursor", "hasMore", "limit"],
        "properties": {
            "nextCursor": {"type": ["string", "null"]},
            "hasMore": {"type": "boolean"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 100},
        },
    },
    "Health": {
        "type": "object",
        "additionalProperties": False,
        "required": ["status", "version"],
        "properties": {
            "status": {"type": "string", "enum": ["healthy", "degraded"]},
            "version": {"type": "string"},
        },
    },
    "Probe": {
        "type": "object",
        "additionalProperties": False,
        "required": ["status"],
        "properties": {
            "status": {"type": "string"},
        },
    },
}


def configure_openapi(app: FastAPI, *, service_name: str) -> None:
    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title="Cloud Content Hub AI REST API",
            version=app.version,
            summary="Public v1 contract; success envelopes and RFC 9457-compatible failures.",
            routes=app.routes,
        )
        schema["openapi"] = "3.1.0"
        schema.setdefault("info", {})["x-service-name"] = service_name
        schema.setdefault("components", {}).setdefault("securitySchemes", {}).update(
            SECURITY_SCHEMES
        )
        schema.setdefault("components", {}).setdefault("parameters", {}).update(COMMON_HEADERS)
        schema.setdefault("components", {}).setdefault("responses", {}).update(PROBLEM_RESPONSES)
        schema.setdefault("components", {}).setdefault("schemas", {}).update(COMPONENT_SCHEMAS)
        schema["security"] = [{"bearerAuth": []}]
        schema.setdefault("tags", [])
        tag_names = {
            "Health",
            "Assets",
            "Content",
            "Publishing",
            "Scheduler",
            "Analytics",
            "Notifications",
            "Admin",
        }
        existing = {
            tag["name"] for tag in schema["tags"] if isinstance(tag, dict) and "name" in tag
        }
        for name in sorted(tag_names - existing):
            schema["tags"].append({"name": name})
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi  # type: ignore[method-assign]

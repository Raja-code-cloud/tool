"""Deterministic constants for end-to-end workflow tests."""

from __future__ import annotations

from uuid import UUID

DEFAULT_WORKSPACE_ID = UUID("01900000-0000-7000-8000-000000000001")
DEFAULT_USER_ID = UUID("01900000-0000-7000-8000-000000000010")
WORKSPACE_ID = DEFAULT_WORKSPACE_ID
USER_ID = DEFAULT_USER_ID

PLATFORM_CODES: tuple[str, ...] = (
    "linkedin",
    "facebook",
    "instagram",
    "x",
    "medium",
    "youtube",
)

SAMPLE_WEBP_BYTES: bytes = (
    b"RIFF$\x00\x00\x00WEBPVP8 \x18\x00\x00\x00\xd0\x0f\x00\x9d\x01*\x01\x00\x01\x00"
    b">\x18\n\xc4\xb4\x00\x00\x00"
)

SAMPLE_PNG_BYTES: bytes = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

SAMPLE_TEXT_BYTES: bytes = (
    b"# Master Article\n\nThis is deterministic seed content for workflow validation.\n"
)

SAMPLE_MP4_BYTES: bytes = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"

WORKFLOW_PERMISSIONS: frozenset[str] = frozenset(
    {
        "assets:read",
        "assets:write",
        "assets:delete",
        "content:read",
        "content:write",
        "content:generate",
        "content:delete",
        "publishing:read",
        "publishing:write",
        "publishing:delete",
        "schedule:read",
        "schedule:write",
        "schedule:delete",
        "analytics:read",
        "notifications:read",
        "notifications:write",
        "admin:read",
        "admin:write",
        "profile:read",
    }
)

ADMIN_PERMISSIONS: frozenset[str] = frozenset({"*", "admin:read", "admin:write"})

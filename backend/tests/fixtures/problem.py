"""Assertions for RFC 9457 problem detail responses."""

from __future__ import annotations

from typing import Any


def assert_problem_response(
    body: dict[str, Any],
    *,
    status: int,
    code: str | None = None,
) -> None:
    """Validate the v1 failure envelope and optional stable error code."""

    assert body["success"] is False
    assert "error" in body
    assert isinstance(body["error"]["message"], str)
    assert body["error"]["message"]
    if code is not None:
        assert body["error"]["code"] == code
    if "status" in body:
        assert body["status"] == status
    if "type" in body:
        assert body["type"].startswith("https://api.cloudcontenthub.ai/problems/")


def assert_success_envelope(body: dict[str, Any], *, message: str | None = None) -> None:
    """Validate the v1 success envelope."""

    assert body["success"] is True
    assert isinstance(body["message"], str)
    assert "data" in body
    assert "meta" in body
    assert "requestId" in body["meta"]
    if message is not None:
        assert body["message"] == message

"""Shared fixtures for stress validation."""

from __future__ import annotations

import pytest

from tests.performance.conftest import (  # noqa: F401
    asset_dto,
    celery_broker,
    event_config,
    mock_handlers,
    perf_headers,
    principal_token,
    storage_provider,
)

pytestmark = pytest.mark.stress

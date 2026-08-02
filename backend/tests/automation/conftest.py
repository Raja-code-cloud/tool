"""Shared fixtures for workflow automation tests."""

from __future__ import annotations

import pytest

pytest_plugins = [
    "tests.fixtures.app",
    "tests.e2e.conftest",
]

pytestmark = [pytest.mark.automation, pytest.mark.integration]

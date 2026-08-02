"""Shared fixtures for API automation tests."""

from __future__ import annotations

import pytest

pytest_plugins = ["tests.fixtures.app"]
pytestmark = pytest.mark.api

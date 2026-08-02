"""Shared fixtures for stress validation."""

from __future__ import annotations

import pytest

pytest_plugins = ["tests.performance.conftest"]

pytestmark = pytest.mark.stress

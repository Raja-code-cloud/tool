"""Shared pytest configuration for backend unit tests."""

from __future__ import annotations

import sys
from pathlib import Path

_TESTS_ROOT = Path(__file__).resolve().parent
if str(_TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_TESTS_ROOT))

pytest_plugins = ["tests.performance.fixtures"]


def pytest_configure() -> None:
    """Preload repository modules before application event imports."""

    from cloud_content_hub.infrastructure.events.registry import create_default_registry

    create_default_registry()

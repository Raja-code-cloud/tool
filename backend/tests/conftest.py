"""Shared pytest configuration for backend unit tests."""

from __future__ import annotations


def pytest_configure() -> None:
    """Preload repository modules before application event imports."""

    from cloud_content_hub.infrastructure.events.registry import create_default_registry

    create_default_registry()

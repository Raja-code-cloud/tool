"""Import utilities for test modules."""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
from types import ModuleType


def load_module_from_file(module_name: str, relative_path: str) -> ModuleType:
    """Load a Python module directly from a file path under ``src/cloud_content_hub``."""

    src_root = Path(__file__).resolve().parents[1] / "src" / "cloud_content_hub"
    file_path = src_root / relative_path
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def try_import_root_router() -> ModuleType | None:
    """Return the v1 root router module when application imports succeed."""

    try:
        return importlib.import_module("cloud_content_hub.api.routers.v1.router")
    except ImportError:
        return None

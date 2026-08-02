"""Safe imports for application modules with interface/event circular dependencies."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from types import ModuleType

import cloud_content_hub


def preload_repository_module(relative_path: str, module_name: str) -> ModuleType:
    """Load a repository module file without executing ``interfaces/__init__.py``."""

    if module_name in sys.modules:
        return sys.modules[module_name]

    root = Path(cloud_content_hub.__file__).resolve().parent
    file_path = root / relative_path
    parts = module_name.split(".")

    for index in range(1, len(parts)):
        package_name = ".".join(parts[:index])
        if package_name in sys.modules:
            continue
        package_path = root.joinpath(*parts[1:index])
        package = types.ModuleType(package_name)
        if package_path.is_dir():
            package.__path__ = [str(package_path)]
        sys.modules[package_name] = package

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        msg = f"Unable to load module spec for {module_name}"
        raise ImportError(msg)

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

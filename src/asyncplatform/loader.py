# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import importlib.util

from pathlib import Path
from typing import Any

from asyncplatform import exceptions


class Loader:
    """Dynamic module loader with caching for efficient class instantiation.

    The Loader class provides a mechanism to dynamically load and cache classes
    from Python modules, avoiding repeated imports. It's designed for plugin-style
    architectures where classes are loaded on-demand from a specific directory.

    Thread Safety:
        This class is safe for use in asyncio (single-threaded event loop)
        applications but is NOT thread-safe for multi-threaded environments.
        The check-then-act caching pattern relies on sequential execution
        provided by the asyncio event loop.
    """

    def __init__(self, path: Path | str, class_name: str) -> None:
        """Initialize the Loader with a base path and class name.

        Args:
            path: Base directory path where modules are located
            class_name: Name of the class to load from each module
        """
        self.path = Path(path)
        self.class_name = class_name
        self._cache: dict[str, type] = {}

    def get(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Load and instantiate a class from a module with caching.

        Dynamically imports a module by name, extracts the configured class,
        caches it for future use, and returns a new instance. Subsequent calls
        with the same name use the cached class definition.

        Args:
            name: Module name (without .py extension) to load
            *args: Positional arguments passed to class constructor
            **kwargs: Keyword arguments passed to class constructor

        Returns:
            New instance of the loaded class

        Raises:
            AsyncPlatformError: If module cannot be loaded or class not found
        """
        if name not in self._cache:
            module_path = self.path / f"{name}.py"

            spec = importlib.util.spec_from_file_location(name, module_path)
            if spec is None or spec.loader is None:
                msg = f"Failed to load module '{name}' from: {module_path}"
                raise exceptions.AsyncPlatformError(msg)

            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except Exception as exc:
                msg = f"Failed to execute module {name}: {exc}"
                raise exceptions.AsyncPlatformError(msg) from exc

            if not hasattr(module, self.class_name):
                msg = f"Module '{name}' does not contain class '{self.class_name}'"
                raise exceptions.AsyncPlatformError(msg)

            self._cache[name] = getattr(module, self.class_name)

        return self._cache[name](*args, **kwargs)


services_loader = Loader(Path(__file__).parent / "services", "Service")
resources_loader = Loader(Path(__file__).parent / "resources", "Resource")

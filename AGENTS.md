# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**asyncplatform** is an async Python client library for the Itential Platform REST API. It provides a high-level interface for interacting with Itential automation platform services, specifically designed for asynchronous operations.

## Technology Stack

- **Language**: Python 3.10+ (supports 3.10, 3.11, 3.12, 3.13)
- **Build System**: Hatchling with uv-dynamic-versioning
- **Dependency Management**: uv (see uv.lock)
- **Core Dependencies**: ipsdk
- **Dev Dependencies**: pytest, pytest-cov, pytest-asyncio, ruff, mypy, coverage, build, bandit, pre-commit, tox

## Development Commands

### Testing
```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/asyncplatform

# Run async tests specifically
uv run pytest -m asyncio
```

### Code Quality
```bash
# Run linting
uv run ruff check

# Auto-fix linting issues
uv run ruff check --fix

# Type checking
uv run mypy src/asyncplatform

# Format code
uv run ruff format
```

### Build and Package
```bash
# Build the package
uv run python -m build

# Install development dependencies
uv sync --group dev
```

### Make Shortcuts
```bash
make test        # Run test suite (verbose)
make coverage    # Run tests with HTML coverage report
make lint        # Lint src/ and tests/
make security    # Run bandit security analysis
make premerge    # Run full premerge checks locally
make tox         # Test across Python 3.10–3.13
make clean       # Remove build artifacts
```

## Architecture

### Core Components

**Client Architecture**: The main `Client` class (`src/asyncplatform/client.py:17`) uses a plugin-based architecture where services are dynamically loaded from the `services/` directory. Each service provides specialized functionality for different Itential Platform services.

**Service System**: Services are discovered and loaded automatically from `src/asyncplatform/services/`. Each service module must contain a `Service` class that inherits from `ServiceBase` and accepts a `Context` object. Services are accessible as attributes on the main client instance (e.g., `client.automation_studio`, `client.authorization`).

**Resource System**: Resources are high-level abstractions that combine multiple services to perform complex operations. They are loaded on-demand using `client.resource("name")`. Resources inherit from `ResourceBase` and have access to services via properties.

**Context Sharing**: A `Context` class (`src/asyncplatform/context.py:17`) provides shared state between services, including:
- The underlying ipsdk AsyncPlatform client connection (`self.client: ipsdk.AsyncPlatform | None`)
- Async cleanup method that properly releases resources

**Dynamic Loading**: The `Loader` class (`src/asyncplatform/loader.py:16`) provides efficient module caching to avoid repeated imports. Two loaders are instantiated:
- `services_loader`: Loads Service classes from `services/`
- `resources_loader`: Loads Resource classes from `resources/`

### Current Services

- **automation_studio**: Manage projects and workflows (import, delete, patch, describe)
- **authorization**: Manage authorization groups and user accounts
- **configuration_manager**: Manage platform configuration
- **lifecycle_manager**: Manage platform lifecycle operations
- **operations_manager**: Manage platform operations
- **help**: Access platform help and documentation

### Current Resources

- **projects**: Import projects with member assignments, delete by name
- **automations**: High-level automation management

### Service Base Class

All services inherit from `ServiceBase` (`src/asyncplatform/services/__init__.py:18`) which provides:
- HTTP method helpers: `get()`, `post()`, `put()`, `patch()`, `delete()`
- Comprehensive exception handling with proper error chaining
- Automatic status code validation
- Consistent error messages for connection/timeout issues

### Usage Patterns

```python
import asyncplatform
from asyncplatform.models.projects import ProjectMember

# Configure connection
cfg = {
    "host": "platform.example.com",
    "user": "admin@domain",
    "password": "secure_password"
}

# Use context manager for proper cleanup
async with asyncplatform.client(**cfg) as client:
    # Access services through client attributes
    projects = await client.automation_studio.get_projects()

    # Use resources for complex operations
    projects_resource = client.resource("projects")
    members = [ProjectMember(name="admin_group", type="group", role="owner")]
    await projects_resource.importer(project_data, members=members)
```

### Key Files

- `src/asyncplatform/client.py`: Main client class and service loading logic
- `src/asyncplatform/context.py`: Shared context with cleanup handling
- `src/asyncplatform/loader.py`: Dynamic module loading with caching
- `src/asyncplatform/services/`: Directory for platform service implementations
- `src/asyncplatform/services/__init__.py`: ServiceBase class for all services
- `src/asyncplatform/resources/`: Directory for high-level resource abstractions
- `src/asyncplatform/resources/__init__.py`: ResourceBase class for all resources
- `src/asyncplatform/logging.py`: Logging configuration and utilities
- `src/asyncplatform/exceptions.py`: Custom exception classes
- `src/asyncplatform/jsonutils.py`: JSON utilities for API responses
- `src/asyncplatform/http.py`: HTTP enumerations and response wrapper
- `src/asyncplatform/heuristics.py`: Heuristic utilities
- `src/asyncplatform/metadata.py`: Package metadata
- `src/asyncplatform/models/`: Data models (e.g., ProjectMember)
- `examples/import_project.py`: Example usage patterns

## Development Notes

### Test Structure

- Tests live in `tests/unit/` (flat layout, not mirroring `src/`)
- Test files named `test_<module>.py` (e.g., `test_services_authorization.py`)
- `tox.ini` configures multi-version testing across Python 3.10–3.13

### Code Style and Type Annotations

- **Python 3.10+ Required**: All code uses modern Python 3.10+ features
- **Future Annotations**: All modules must include `from __future__ import annotations` at the top
- **Type Hints**: Use modern union syntax (`str | None` not `Optional[str]`)
- **Use Built-in Types**: Prefer `dict`, `list`, `tuple` over `typing.Dict`, `List`, `Tuple`
- **Import Collections**: Use `collections.abc.Mapping`, `collections.abc.Callable` for abstract types
- **TYPE_CHECKING**: Use `from typing import TYPE_CHECKING` for import-only type hints to avoid circular dependencies

### Service Development

- All services must implement a `Service` class that inherits from `ServiceBase`
- Services accept a `Context` object in `__init__(self, ctx: Context)`
- Access the ipsdk client via `self.ctx.client`
- Use inherited HTTP methods: `await self.get(path, params=...)`, `await self.post(path, json=...)`
- The client uses `ipsdk.platform_factory(want_async=True)` for async operations

### Resource Development

- All resources must implement a `Resource` class that inherits from `ResourceBase`
- Resources accept a `Client` object in `__init__(self, client: Client)`
- Access services via properties: `self.studio`, `self.authorization`
- Combine multiple service calls to provide high-level functionality
- Use caching for expensive operations (groups, accounts)

### Error Handling

- Use custom exceptions from `src/asyncplatform/exceptions.py`:
  - `AsyncPlatformError`: Base exception for all SDK errors
  - `NotFoundError`: Resource not found errors
  - `SerializationError`: JSON parsing/serialization errors
- ServiceBase automatically wraps ipsdk exceptions with proper error chaining
- Always use `raise ... from exc` to preserve exception context
- Log exceptions in cleanup methods but don't propagate them

### Documentation Standards

- **Docstrings**: Use Google-style documentation strings for all public methods
- **Required Sections**: All docstrings must include `Args:`, `Returns:`, `Raises:`
- **Type Documentation**: Don't repeat type information in docstrings (use type hints instead)
- **Exception Documentation**: Only document exceptions that the function/method can raise
- **Be Concise**: Focus on "why" rather than "what" (code shows what, docs explain why)

### Logging

- Use the logging module: `from asyncplatform import logging`
- Trace function calls: `logging.trace(self.method_name)`
- Log important operations: `logging.info(f"Operation completed: {details}")`
- Warn on unexpected states: `logging.warning(f"Unexpected: {issue}")`
- Don't use print statements - use appropriate logging levels

### Licensing

- All Python files must include GPL-3.0 header:
  ```python
  # Copyright (c) 2025 Itential, Inc
  # GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
  # SPDX-License-Identifier: GPL-3.0-or-later
  ```

### Best Practices

- Use async context managers (`async with`) for proper resource cleanup
- Leverage `asyncio.gather()` for concurrent operations with proper error handling
- Keep methods focused on a single responsibility
- Use pathlib for file operations
- Prefer `pathlib.glob()` over manual iteration for file discovery
- Use dictionary comprehensions to filter None values from kwargs

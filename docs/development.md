# Development Setup Guide

This guide covers everything you need to set up a development environment for AsyncPlatform.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Development Tools](#development-tools)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Quality](#code-quality)
- [Building and Publishing](#building-and-publishing)

## Prerequisites

### Required Software

- **Python 3.10 or higher**
  ```bash
  python --version  # Should be 3.10+
  ```

- **uv** (Python package manager)
  ```bash
  # Install uv if not already installed
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Verify installation
  uv --version
  ```

- **git** (version control)
  ```bash
  git --version
  ```

### Optional but Recommended

- **make** (build automation)
- **vim** or your preferred editor
- **direnv** (for environment management)

## Initial Setup

### 1. Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd asyncplatform

# Check the current branch
git branch
```

### 2. Install Dependencies

```bash
# Install all dependencies including dev dependencies
uv sync --group dev

# This installs:
# - Core dependencies (ipsdk)
# - Dev dependencies (pytest, ruff, mypy, etc.)
# - The package itself in editable mode
```

### 3. Verify Installation

```bash
# Run tests to verify everything works
make test

# Should see: ===== 427 passed in X.XXs =====
```

## Development Tools

### uv Commands

```bash
# Sync dependencies
uv sync

# Install a new dependency
uv add <package-name>

# Install a dev dependency
uv add --group dev <package-name>

# Run a command in the uv environment
uv run <command>

# Example: Run pytest
uv run pytest
```

### Make Commands

The project includes a Makefile with common development tasks:

```bash
# Run tests
make test

# Run tests with coverage
make coverage

# Run linting
make lint

# Run security checks
make security

# Format code
make format

# Auto-fix linting issues
make ruff-fix

# Run all pre-merge checks (clean, lint, security, test)
make premerge

# Clean build artifacts
make clean

# See all available commands
make help
```

### Code Quality Tools

**Ruff** - Fast Python linter and formatter

```bash
# Check code
uv run ruff check src/asyncplatform

# Auto-fix issues
uv run ruff check --fix src/asyncplatform

# Format code
uv run ruff format src/asyncplatform
```

**Mypy** - Static type checker

```bash
# Check types in source code
uv run mypy src/asyncplatform

# Check types in tests (uses pyproject.toml configuration)
uv run mypy tests
```

**Bandit** - Security vulnerability scanner

```bash
# Run security checks
uv run bandit -r src/asyncplatform --configfile pyproject.toml
```

**Pytest** - Testing framework

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=src/asyncplatform

# Run specific test file
uv run pytest tests/unit/test_client.py

# Run specific test
uv run pytest tests/unit/test_client.py::TestClientInitialization::test_client_initialization_with_defaults
```

## Project Structure

```
asyncplatform/
├── src/asyncplatform/          # Main source code
│   ├── __init__.py             # Package initialization
│   ├── __main__.py             # CLI entry point
│   ├── client.py               # Main client class
│   ├── context.py              # Shared context
│   ├── loader.py               # Dynamic module loader
│   ├── exceptions.py           # Custom exceptions
│   ├── http.py                 # HTTP enums and helpers
│   ├── jsonutils.py            # JSON utilities
│   ├── logging.py              # Logging system
│   ├── metadata.py             # Package metadata
│   ├── heuristics.py           # Pattern detection
│   ├── services/               # Platform services
│   │   ├── __init__.py         # ServiceBase class
│   │   ├── automation_studio.py
│   │   ├── authorization.py
│   │   └── operations_manager.py
│   ├── resources/              # High-level resources
│   │   ├── __init__.py         # ResourceBase class
│   │   ├── projects.py
│   │   └── automations.py
│   └── models/                 # Data models
│       ├── __init__.py
│       └── projects.py
├── tests/                      # Test suite
│   └── unit/                   # Unit tests
│       ├── test_client.py
│       ├── test_services_*.py
│       └── test_resources_*.py
├── examples/                   # Usage examples
│   └── import_project.py
├── docs/                       # Documentation
│   ├── README.md
│   ├── getting-started.md
│   ├── architecture.md
│   ├── development.md          # This file
│   ├── testing.md
│   ├── contributing.md
│   └── examples.md
├── pyproject.toml              # Project configuration
├── uv.lock                     # Locked dependencies
├── Makefile                    # Build automation
├── CLAUDE.md                   # Project guidelines
├── LICENSE                     # GPL-3.0 license
└── README.md                   # Project README
```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Start from the devel branch
git checkout devel
git pull origin devel

# Create feature branch
git checkout -b feature/my-new-feature
```

### 2. Make Changes

Edit files using your preferred editor:

```bash
# Example: Add a new service
vim src/asyncplatform/services/my_service.py
```

### 3. Run Tests Continuously

While developing, run tests frequently:

```bash
# Run tests for the file you're working on
uv run pytest tests/unit/test_my_service.py -v

# Run all tests
make test
```

### 4. Check Code Quality

Before committing:

```bash
# Run all pre-merge checks
make premerge

# This runs:
# - make clean (clean build artifacts)
# - make lint (ruff check)
# - make security (bandit)
# - make test (pytest)
```

### 5. Commit Changes

```bash
# Stage changes
git add src/asyncplatform/services/my_service.py
git add tests/unit/test_my_service.py

# Create commit
git commit -m "Add my_service for managing XYZ

Implements the following methods:
- get_items(): Retrieve all items
- create_item(): Create new item

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 6. Push and Create PR

```bash
# Push branch
git push -u origin feature/my-new-feature

# Create pull request (if gh CLI is installed)
gh pr create --title "Add my_service" --body "Description of changes"
```

## Code Quality

### Code Style

The project follows these conventions:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Type hints**: Required for all public APIs
- **Docstrings**: Google-style for all public functions/classes

### Type Hints

Always use modern type hint syntax:

```python
# Good
def my_function(name: str, age: int | None = None) -> dict[str, Any]:
    pass

# Bad
from typing import Optional, Dict, Any
def my_function(name: str, age: Optional[int] = None) -> Dict[str, Any]:
    pass
```

### Docstring Format

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """Brief description of the function.

    Longer description if needed, explaining what the function does
    and any important details.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
        AsyncPlatformError: When API call fails
    """
    pass
```

### License Headers

All Python files must include the GPL-3.0 header:

```python
# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
```

### Import Organization

Organize imports in this order:

```python
# 1. Future imports
from __future__ import annotations

# 2. Standard library
import asyncio
import json
from typing import TYPE_CHECKING

# 3. Third-party
import ipsdk

# 4. Local imports
from . import exceptions
from . import logging

# 5. TYPE_CHECKING imports
if TYPE_CHECKING:
    from collections.abc import Mapping
```

## Building and Publishing

### Building the Package

```bash
# Build source and wheel distributions
uv run python -m build

# Output in dist/
# - asyncplatform-X.Y.Z.tar.gz (source)
# - asyncplatform-X.Y.Z-py3-none-any.whl (wheel)
```

### Version Management

Version is managed via git tags using `uv-dynamic-versioning`:

```bash
# Create a new version tag
git tag v0.1.0
git push origin v0.1.0

# The version is automatically derived from the latest tag
```

### Running Tox

Test across multiple Python versions:

```bash
# Test all supported versions (3.10, 3.11, 3.12, 3.13)
uv run tox

# Test specific version
uv run tox -e py310
uv run tox -e py312
```

## Troubleshooting

### Import Errors After Adding Dependencies

```bash
# Resync dependencies
uv sync --group dev
```

### Tests Fail After Checkout

```bash
# Clean and reinstall
make clean
uv sync --group dev
make test
```

### Type Checking Errors

```bash
# Run mypy to see type errors
uv run mypy src/asyncplatform

# Common issues:
# - Missing return type hints
# - Using old typing syntax (Dict vs dict)
# - Missing TYPE_CHECKING imports
```

### Coverage Reports Not Generated

```bash
# Clean coverage data
rm -f .coverage coverage.xml
rm -rf htmlcov/

# Rerun coverage
make coverage

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Editor Setup

### VS Code

Recommended `settings.json`:

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false
}
```

### Vim

Add to your `.vimrc`:

```vim
" Use ruff for Python linting
autocmd FileType python setlocal makeprg=ruff\ check\ %
autocmd FileType python setlocal errorformat=%f:%l:%c:\ %m

" Run tests on save
autocmd BufWritePost */test_*.py silent !pytest <afile>
```

## Next Steps

- Read the [Testing Guide](testing.md) to learn about writing tests
- Review the [Contributing Guide](contributing.md) for contribution guidelines
- Check out [Examples](examples.md) for usage patterns
- Study the [Architecture](architecture.md) to understand the system design

## Additional Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

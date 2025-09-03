# Contributing to AsyncPlatform

Thank you for your interest in contributing to AsyncPlatform! This guide will help you get started with contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Project Architecture](#project-architecture)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project adheres to a code of conduct that promotes a welcoming and inclusive environment. Please be respectful and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.10 or higher (we test on 3.10, 3.11, 3.12)
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/asyncplatform.git
   cd asyncplatform
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/itential/asyncplatform.git
   ```

## Development Setup

### Install Dependencies

```bash
# Install all dependencies including development tools
uv sync

# Verify installation
uv run python --version
uv run pytest --version
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code quality:

```bash
uv run pre-commit install
```

This will run linting, formatting, and security checks before each commit.

## Development Workflow

### Branch Strategy

- `devel` - Main development branch
- `feature/your-feature` - Feature branches
- `fix/issue-description` - Bug fix branches
- `security/security-improvement` - Security-related changes

### Creating a Feature Branch

```bash
git checkout devel
git pull upstream devel
git checkout -b feature/your-feature-name
```

### Making Changes

1. Make your changes in small, logical commits
2. Follow the [code standards](#code-standards)
3. Add or update tests as needed
4. Update documentation if required
5. Run the development checks frequently

### Development Commands

```bash
# Run all linting checks
uv run ruff check src/asyncplatform tests

# Auto-format code
uv run ruff format src/asyncplatform tests

# Auto-fix linting issues where possible
uv run ruff check --fix src/asyncplatform tests

# Run tests
uv run pytest tests

# Run tests with coverage
uv run pytest --cov=src/asyncplatform --cov-report=term --cov-report=html tests/

# Run security analysis
uv run bandit -r src/asyncplatform --configfile pyproject.toml

# Run type checking
uv run mypy src/asyncplatform
```

### Testing Different Python Versions

```bash
# Test specific Python version
uv run --python 3.10 pytest tests
uv run --python 3.11 pytest tests
uv run --python 3.12 pytest tests

# Test all supported versions
for version in 3.10 3.11 3.12; do
    echo "Testing Python $version"
    uv run --python $version pytest tests
done
```

## Project Architecture

AsyncPlatform uses a plugin-based architecture for organizing code:

### Services

- Located in `src/asyncplatform/services/`
- Each service provides functionality for specific Itential Platform APIs
- Services inherit from `ServiceBase` which provides HTTP method helpers
- Services are automatically loaded and attached to the client instance
- Example: `client.automation_studio.get_projects()`

### Resources

- Located in `src/asyncplatform/resources/`
- Resources combine multiple services to provide high-level operations
- Resources inherit from `ResourceBase` and have access to all services
- Resources are loaded on-demand using `client.resource("name")`
- Example: `client.resource("projects").importer(...)`

### Context and Caching

- `Context` class provides shared state between services
- Includes the underlying ipsdk client connection
- Provides async-safe caching with TTL support
- Context is properly cleaned up on client close

### Dynamic Loading

- `Loader` class handles dynamic module loading with caching
- Thread-safe for asyncio (single-threaded event loop) applications
- Not thread-safe for multi-threaded environments

## Code Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) for Python code style
- Use [Black](https://black.readthedocs.io/)-compatible formatting (88 character line length)
- Code is automatically formatted using Ruff

### Code Quality

- **Linting**: We use Ruff with comprehensive rule sets
- **Type Hints**: All public APIs must include type hints using Python 3.10+ syntax
  - Use `from __future__ import annotations` at the top of all modules
  - Prefer `str | None` over `Optional[str]`
  - Prefer `dict`, `list`, `tuple` over `typing.Dict`, `List`, `Tuple`
- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Security**: All code is scanned with Bandit and Ruff security rules
- **Async Code**: This is an async library - follow asyncio best practices
- **Error Handling**: Always use `raise ... from exc` to preserve exception context

### Licensing

All Python files must include the GPL-3.0 license header:

```python
# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
```

### Docstring Format

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """Brief description of what the function does.

    Longer description if needed, explaining the function's behavior,
    usage patterns, or important considerations.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter with default value.

    Returns:
        Description of the return value and its type.

    Raises:
        ValueError: When param1 is invalid.
        ConnectionError: When unable to connect to the server.

    Example:
        >>> result = example_function("test", 20)
        >>> print(result)
        True
    """
```

### Import Organization

- Follow the import order: standard library, third-party, local
- Use absolute imports
- One import per line
- Always include `from __future__ import annotations` as the first import

```python
from __future__ import annotations

# Standard library
from pathlib import Path
from typing import Any

# Third-party
import ipsdk

# Local
from asyncplatform import exceptions
from asyncplatform.context import Context
```

## Testing

### Test Structure

- Tests are located in the `tests/` directory
- Test files follow the pattern `test_<module>.py`
- Each module should have comprehensive test coverage

### Writing Tests

```python
import pytest
import asyncplatform


@pytest.mark.asyncio
async def test_client_initialization():
    """Test basic client initialization."""
    cfg = {
        "host": "test.example.com",
        "user": "test_user",
        "password": "test_pass"
    }
    async with asyncplatform.client(**cfg) as client:
        assert client is not None


@pytest.mark.asyncio
async def test_service_loading():
    """Test that services are loaded correctly."""
    cfg = {
        "host": "test.example.com",
        "user": "test_user",
        "password": "test_pass"
    }
    async with asyncplatform.client(**cfg) as client:
        assert hasattr(client, "automation_studio")
        assert hasattr(client, "authorization")
```

### Coverage Requirements

- High test coverage is required
- All new code must include tests
- Tests should cover both success and failure scenarios
- Tests should cover edge cases and error conditions
- Use mocks appropriately for external dependencies

### Running Tests

```bash
# Run all tests
uv run pytest tests

# Run specific test file
uv run pytest tests/unit/test_loader.py

# Run specific test function
uv run pytest tests/unit/test_loader.py::TestLoaderInitialization::test_loader_init_with_valid_path

# Run with verbose output
uv run pytest -v tests

# Run with coverage reporting
uv run pytest --cov=src/asyncplatform --cov-report=term tests

# Run async tests specifically
uv run pytest -m asyncio tests
```

## Documentation

### Code Documentation

- All public APIs must have docstrings
- Use Google-style docstrings
- Include examples in docstrings where helpful
- Document all parameters, return values, and exceptions

### README Updates

- Update README.md if your changes affect:
  - Installation instructions
  - Usage examples
  - API changes
  - New features

### Changelog

- The project uses [conventional commits](https://www.conventionalcommits.org/) for automatic changelog generation
- Changelog is generated automatically using git-cliff
- Use descriptive commit messages following the conventional format:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation changes
  - `test:` for test improvements
  - `ci:` for CI/CD changes
  - `refactor:` for code refactoring

## Submitting Changes

### Before Submitting

1. Ensure all tests pass: `uv run pytest tests`
2. Run linting: `uv run ruff check src/asyncplatform tests`
3. Run type checking: `uv run mypy src/asyncplatform`
4. Format code: `uv run ruff format src/asyncplatform tests`
5. Update documentation if needed
6. Write descriptive commit messages

### Pull Request Process

1. Push your feature branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a pull request against the `devel` branch

3. Fill out the pull request template with:
   - Clear description of changes
   - Testing performed
   - Any breaking changes
   - Related issues

### Pull Request Requirements

- All tests must pass
- All linting checks must pass
- Type checking must pass
- Code must be properly formatted
- At least one maintainer approval required
- All conversations must be resolved

### Commit Message Format

Use conventional commit format:

```
type(scope): description

Longer explanation if needed.

- List any breaking changes
- Reference related issues

```

## Release Process

### Versioning

- Uses [Semantic Versioning](https://semver.org/)
- Version is automatically determined from git tags using uv-dynamic-versioning
- Format: `v<major>.<minor>.<patch>` (e.g., `v1.0.0`)

### Creating a Release

Releases are managed by project maintainers:

1. Ensure all tests pass and code quality checks succeed
2. Update CHANGELOG.md if needed
3. Create and push a version tag:
   ```bash
   git tag v1.0.0
   git push upstream v1.0.0
   ```

### Building Locally

To test the build process locally:

```bash
# Build distribution packages
uv run python -m build

# Verify the build artifacts
ls -l dist/
```

## Getting Help

### Resources

- [AsyncPlatform Documentation](https://github.com/itential/asyncplatform)
- [Itential Platform Documentation](https://docs.itential.com/)
- [Project Issues](https://github.com/itential/asyncplatform/issues)

### Contact

- Create an issue for bugs or feature requests
- Use discussions for questions and community interaction
- Follow the security policy for security-related issues

### Development Environment Issues

If you encounter issues with the development environment:

1. Ensure you have the latest version of uv
2. Try cleaning and reinstalling dependencies:
   ```bash
   rm -rf .venv
   uv sync
   ```
3. Check that all required Python versions are available
4. Verify pre-commit hooks are installed

## Thank You

Thank you for contributing to AsyncPlatform! Your contributions help make the project better for everyone.

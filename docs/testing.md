# Testing Guide

This guide covers testing practices, patterns, and strategies for AsyncPlatform.

## Table of Contents

- [Overview](#overview)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Testing Patterns](#testing-patterns)
- [Mocking Strategies](#mocking-strategies)
- [Coverage](#coverage)
- [Best Practices](#best-practices)

## Overview

AsyncPlatform uses **pytest** for testing with the following characteristics:

- **427 unit tests** covering 99.63% of code
- **Fast execution**: ~1 second for full test suite
- **Async support**: pytest-asyncio for async tests
- **Isolated tests**: Each test is independent
- **Comprehensive mocking**: No external dependencies

### Test Philosophy

1. **Unit tests only**: No integration tests currently
2. **Mock external dependencies**: ipsdk client is always mocked
3. **Test behavior, not implementation**: Focus on public APIs
4. **Descriptive test names**: Tests serve as documentation
5. **AAA pattern**: Arrange, Act, Assert

## Running Tests

### Basic Test Execution

```bash
# Run all tests
make test

# Or directly with pytest
uv run pytest

# With verbose output
uv run pytest -v

# With output from print statements
uv run pytest -s
```

### Running Specific Tests

```bash
# Run specific test file
uv run pytest tests/unit/test_client.py

# Run specific test class
uv run pytest tests/unit/test_client.py::TestClientInitialization

# Run specific test method
uv run pytest tests/unit/test_client.py::TestClientInitialization::test_client_initialization_with_defaults

# Run tests matching pattern
uv run pytest -k "test_client"
```

### Coverage Reports

```bash
# Run tests with coverage
make coverage

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Coverage summary
uv run pytest --cov=src/asyncplatform --cov-report=term
```

## Writing Tests

### Test File Structure

Tests are organized in `tests/unit/` with a `test_` prefix:

```
tests/unit/
├── test_client.py              # Client tests
├── test_context.py             # Context tests
├── test_services_base.py       # ServiceBase tests
├── test_services_automation_studio.py
├── test_services_authorization.py
├── test_services_operations_manager.py
├── test_resources_base.py      # ResourceBase tests
├── test_resources_projects.py
└── test_*.py                   # Other module tests
```

### Basic Test Template

```python
# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.mymodule module."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from asyncplatform import mymodule


class TestMyClass:
    """Test suite for MyClass."""

    def test_basic_functionality(self):
        """Test basic functionality of MyClass.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Arrange
        obj = mymodule.MyClass()

        # Act
        result = obj.method()

        # Assert
        assert result == expected_value


class TestMyAsyncClass:
    """Test suite for async functionality."""

    @pytest.mark.asyncio
    async def test_async_method(self):
        """Test async method.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Arrange
        obj = mymodule.MyAsyncClass()

        # Act
        result = await obj.async_method()

        # Assert
        assert result == expected_value
```

### Testing Async Code

Use `@pytest.mark.asyncio` for async tests:

```python
@pytest.mark.asyncio
async def test_get_projects(self):
    """Test getting projects."""
    ctx = context.Context()
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": []}
    mock_client.get = AsyncMock(return_value=mock_response)
    ctx.client = mock_client

    service = Service(ctx)
    result = await service.get_projects()

    assert isinstance(result, list)
    mock_client.get.assert_called_once()
```

## Testing Patterns

### Pattern 1: Testing Services

Services depend on `Context` with an ipsdk client:

```python
from asyncplatform import context
from asyncplatform.services.automation_studio import Service

class TestAutomationStudioService:
    """Test suite for Automation Studio service."""

    @pytest.mark.asyncio
    async def test_get_projects(self):
        """Test get_projects returns list of projects."""
        # Create context and mock client
        ctx = context.Context()
        mock_client = MagicMock()

        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "metadata": {"total": 2},
            "data": [
                {"_id": "1", "name": "Project 1"},
                {"_id": "2", "name": "Project 2"}
            ]
        }

        # Setup mock client
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        # Create service and call method
        service = Service(ctx)
        result = await service.get_projects()

        # Assertions
        assert len(result) == 2
        assert result[0]["name"] == "Project 1"
        mock_client.get.assert_called_once()
```

### Pattern 2: Testing Resources

Resources depend on `Client` and access services:

```python
from unittest.mock import MagicMock
from asyncplatform.resources.projects import Resource

class TestProjectsResource:
    """Test suite for Projects resource."""

    @pytest.mark.asyncio
    async def test_delete_project(self):
        """Test deleting a project by name."""
        # Create mock client with services
        mock_client = MagicMock()
        mock_client.automation_studio = MagicMock()

        # Mock find_projects
        mock_client.automation_studio.find_projects = AsyncMock(
            return_value=[{"_id": "proj1", "name": "TestProject"}]
        )

        # Mock delete_project
        mock_client.automation_studio.delete_project = AsyncMock(
            return_value={"message": "Deleted"}
        )

        # Create resource and call method
        resource = Resource(mock_client)
        result = await resource.delete("TestProject")

        # Assertions
        assert result["message"] == "Deleted"
        mock_client.automation_studio.find_projects.assert_awaited_once()
        mock_client.automation_studio.delete_project.assert_awaited_once()
```

### Pattern 3: Testing with Patch

Use `patch` for patching methods:

```python
from unittest.mock import patch

class TestWithPatch:
    """Test using patch decorator."""

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_with_patch(self, mock_get):
        """Test using patch decorator."""
        # Setup mock return value
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response

        # Create service and call
        ctx = context.Context()
        service = Service(ctx)
        result = await service.get_projects()

        # Assertions
        assert isinstance(result, list)
        mock_get.assert_called_once()
```

### Pattern 4: Testing Exceptions

Test error handling and exceptions:

```python
@pytest.mark.asyncio
async def test_raises_not_found_error(self):
    """Test that NotFoundError is raised."""
    ctx = context.Context()
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "metadata": {"total": 0},
        "items": []
    }
    mock_client.get = AsyncMock(return_value=mock_response)
    ctx.client = mock_client

    service = Service(ctx)

    # Use pytest.raises context manager
    with pytest.raises(exceptions.NotFoundError) as exc_info:
        await service.describe_workflow("nonexistent")

    # Assert exception message
    assert "not found" in str(exc_info.value)
```

### Pattern 5: Testing Pagination

Test automatic pagination:

```python
@pytest.mark.asyncio
async def test_handles_pagination(self):
    """Test that pagination is handled automatically."""
    ctx = context.Context()
    mock_client = MagicMock()

    # First page
    first_response = MagicMock()
    first_response.json.return_value = {
        "metadata": {"total": 150},
        "data": [{"_id": str(i)} for i in range(100)]
    }

    # Second page (returned as dict for asyncio.gather)
    second_page = {
        "metadata": {"total": 150},
        "data": [{"_id": str(i)} for i in range(100, 150)]
    }

    # Setup mock to return different values
    mock_client.get = AsyncMock(side_effect=[first_response, second_page])
    ctx.client = mock_client

    service = Service(ctx)
    result = await service.get_projects()

    # Assert all items retrieved
    assert len(result) == 150
    assert mock_client.get.await_count == 2
```

## Mocking Strategies

### Mocking ipsdk Client

The ipsdk client is always mocked in unit tests:

```python
from unittest.mock import MagicMock, AsyncMock

# Create mock client
mock_client = MagicMock()

# Mock async methods
mock_client.get = AsyncMock(return_value=mock_response)
mock_client.post = AsyncMock(return_value=mock_response)
mock_client.put = AsyncMock(return_value=mock_response)
mock_client.patch = AsyncMock(return_value=mock_response)
mock_client.delete = AsyncMock(return_value=mock_response)

# Mock context manager methods
mock_client.connect = AsyncMock()
mock_client.close = AsyncMock()
```

### Mocking HTTP Responses

Mock responses should have a `json()` method:

```python
mock_response = MagicMock()
mock_response.json.return_value = {
    "metadata": {"total": 1},
    "data": [{"_id": "1", "name": "Item"}]
}
mock_response.status_code = 200
```

### Using AsyncMock

For async functions, use `AsyncMock`:

```python
from unittest.mock import AsyncMock

# Create async mock
async_func = AsyncMock(return_value="result")

# Call it
result = await async_func()  # Returns "result"

# Verify it was called
async_func.assert_awaited_once()
async_func.assert_awaited_with(arg1, arg2)
```

### Mocking with side_effect

Use `side_effect` for multiple return values or exceptions:

```python
# Multiple return values
mock_func = AsyncMock(side_effect=[result1, result2, result3])

# Exception then success
mock_func = AsyncMock(side_effect=[Exception("Error"), success_result])

# Dynamic return based on arguments
def side_effect_func(arg):
    if arg == "valid":
        return success_result
    raise ValueError("Invalid argument")

mock_func = AsyncMock(side_effect=side_effect_func)
```

### Coverage Goals

- **Overall**: Maintain 95%+ coverage (enforced by `--cov-fail-under=95`)
- **New code**: Aim for 100% coverage
- **Critical paths**: Must have 100% coverage
- **Error handling**: All error paths must be tested

### Type Checking

The project uses mypy for static type checking. Configuration is in `pyproject.toml`:

```bash
# Check types in tests
uv run mypy tests

# The configuration includes:
# - ignore_missing_imports = true (for packages without stubs)
# - python_version = "3.10"
# - Relaxed checking for test files
```

## Best Practices

### Test Naming

Use descriptive names that explain what is being tested:

```python
# Good
def test_get_projects_returns_empty_list_when_no_projects(self):
    pass

def test_import_project_raises_error_when_project_exists(self):
    pass

# Bad
def test_get_projects(self):
    pass

def test_error(self):
    pass
```

### Test Organization

Group related tests in classes:

```python
class TestClientInitialization:
    """Tests for client initialization."""
    pass

class TestClientServiceLoading:
    """Tests for service loading."""
    pass

class TestClientResourceLoading:
    """Tests for resource loading."""
    pass
```

### Test Independence

Each test should be independent:

```python
# Good - each test is independent
def test_enable_filtering(self):
    enable_filtering()
    assert is_filtering_enabled()

def test_disable_filtering(self):
    enable_filtering()  # Setup state
    disable_filtering()
    assert not is_filtering_enabled()

# Bad - tests depend on execution order
def test_enable_filtering(self):
    enable_filtering()
    assert is_filtering_enabled()

def test_disable_filtering(self):
    # Assumes filtering is already enabled!
    disable_filtering()
    assert not is_filtering_enabled()
```

### Setup and Teardown

Use pytest fixtures for setup/teardown:

```python
import pytest

@pytest.fixture
def mock_client():
    """Create mock client for tests."""
    client = MagicMock()
    client.get = AsyncMock()
    yield client
    # Cleanup if needed

def test_with_fixture(mock_client):
    """Test using fixture."""
    # mock_client is automatically provided
    mock_client.get.return_value = MagicMock()
```

### Docstrings

All test methods should have docstrings:

```python
def test_my_feature(self):
    """Test that my feature works correctly.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    pass
```

### Assertions

Use clear, specific assertions:

```python
# Good - specific assertions
assert result == expected_value
assert len(items) == 3
assert "error" in error_message
assert mock_func.called
assert mock_func.call_count == 2

# Bad - generic assertions
assert result  # What value is expected?
assert items   # How many? What contents?
```

### Testing Private Methods

Generally, test public APIs, not private methods:

```python
# Good - test public API
def test_public_method(self):
    result = obj.public_method()
    assert result == expected

# Bad - testing private implementation
def test_private_method(self):
    result = obj._private_method()
    assert result == expected
```

However, for complex private methods, targeted tests are acceptable.

## Continuous Integration

Tests run automatically on:

- **Pre-merge**: Before merging to devel/main
- **Pre-commit**: Via git hooks (if configured)
- **Manual**: Via `make premerge`

### Pre-merge Checklist

Before creating a PR:

```bash
# 1. Run all pre-merge checks
make premerge

# 2. Verify coverage didn't decrease
make coverage

# 3. Check for new linting issues
make lint

# 4. Run security scan
make security
```

## Troubleshooting Tests

### Tests Fail After Checkout

```bash
make clean
uv sync --group dev
make test
```

### Async Test Warnings

If you see warnings about event loops:

```python
# Ensure @pytest.mark.asyncio is present
@pytest.mark.asyncio
async def test_my_async_function(self):
    pass
```

### Mock Not Working

Verify you're mocking the right location:

```python
# Mock where it's used, not where it's defined
# If module A imports B, mock A.B not B
with patch("asyncplatform.services.module_a.some_function"):
    pass
```

### Coverage Not Updating

```bash
# Clean coverage data
rm -f .coverage
rm -rf htmlcov/

# Rerun
make coverage
```

## Next Steps

- Review [Contributing Guidelines](contributing.md) for code standards
- Study [Examples](examples.md) for usage patterns
- Read [Development Guide](development.md) for environment setup
- Explore [Architecture](architecture.md) for system design

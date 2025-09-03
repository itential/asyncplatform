# Getting Started with AsyncPlatform

This guide will help you get started with AsyncPlatform, from installation to running your first API calls.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or higher** installed
- **uv** package manager (recommended) or pip
- Access to an Itential Platform instance
- Valid credentials for the platform

## Installation

### Using uv (Recommended)

```bash
# Add asyncplatform to your project
uv add asyncplatform
```

### Using pip

```bash
# Install from source
pip install -e .
```

### Development Installation

For development work with all dev dependencies:

```bash
# Clone the repository
git clone <repository-url>
cd asyncplatform

# Install with dev dependencies
uv sync --group dev
```

## Quick Start

### Basic Usage

Here's a simple example to get you started:

```python
import asyncio
import asyncplatform

async def main():
    # Configure connection
    config = {
        "host": "platform.example.com",
        "user": "admin@domain",
        "password": "your_password"
    }

    # Use context manager for proper cleanup
    async with asyncplatform.client(**config) as client:
        # Get all projects
        projects = await client.automation_studio.get_projects()

        for project in projects:
            print(f"Project: {project['name']}")

# Run the async function
asyncio.run(main())
```

### Working with Services

Services provide direct access to platform APIs:

```python
async with asyncplatform.client(**config) as client:
    # Automation Studio service
    projects = await client.automation_studio.get_projects()
    project = await client.automation_studio.describe_project("project_id")

    # Authorization service
    groups = await client.authorization.get_groups()
    accounts = await client.authorization.get_accounts()

    # Operations Manager service
    automations = await client.operations_manager.find_automations(
        name="MyAutomation"
    )
```

### Working with Resources

Resources provide high-level operations that combine multiple services:

```python
from asyncplatform.models.projects import ProjectMember

async with asyncplatform.client(**config) as client:
    # Get the projects resource
    projects = client.resource("projects")

    # Import a project with members
    project_data = {
        "name": "New Project",
        "description": "Project description"
    }

    members = [
        ProjectMember(name="admin_group", type="group", role="owner"),
        ProjectMember(username="john.doe", type="account", role="editor")
    ]

    result = await projects.importer(project_data, members=members)
    print(f"Imported project: {result['name']}")

    # Delete a project by name
    await projects.delete("Old Project")
```

## Configuration Options

The client accepts the following configuration parameters:

```python
config = {
    "host": "platform.example.com",     # Required: Platform hostname
    "user": "admin@domain",              # Required: Username
    "password": "your_password",         # Required: Password
    "port": 443,                         # Optional: Port (default: 0)
    "use_tls": True,                     # Optional: Use TLS/HTTPS (default: True)
    "verify": True,                      # Optional: SSL verification (default: True)
    "timeout": 30,                       # Optional: Request timeout in seconds (default: 30)
    "client_id": "your_client_id",       # Optional: OAuth client ID
    "client_secret": "your_secret",      # Optional: OAuth client secret
}

async with asyncplatform.client(**config) as client:
    # Your code here
    pass
```

## Error Handling

AsyncPlatform uses custom exceptions for error handling:

```python
from asyncplatform import exceptions

try:
    async with asyncplatform.client(**config) as client:
        project = await client.automation_studio.describe_project("invalid_id")
except exceptions.NotFoundError as e:
    print(f"Project not found: {e}")
except exceptions.AsyncPlatformError as e:
    print(f"Platform error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Common Exceptions

- `AsyncPlatformError`: Base exception for all SDK errors
- `NotFoundError`: Resource not found (404)
- `SerializationError`: JSON parsing/serialization errors

## Logging

AsyncPlatform includes a comprehensive logging system:

```python
from asyncplatform import logging

# Set logging level
logging.set_level(logging.INFO)

# Enable TRACE for detailed debugging
logging.set_level(logging.TRACE)

# Disable logging
logging.set_level(logging.NONE)

# Enable sensitive data filtering
logging.enable_sensitive_data_filtering()
```

### Available Log Levels

- `NOTSET` (0)
- `TRACE` (5) - Detailed function tracing
- `DEBUG` (10) - Debug information
- `INFO` (20) - Informational messages
- `WARNING` (30) - Warning messages
- `ERROR` (40) - Error messages
- `CRITICAL` (50) - Critical errors
- `FATAL` (90) - Fatal errors (exits application)
- `NONE` (100) - Disable all logging

## Working with Pagination

Many API endpoints return paginated results. AsyncPlatform handles pagination automatically:

```python
async with asyncplatform.client(**config) as client:
    # This call automatically handles pagination
    # and returns ALL projects, even if there are thousands
    all_projects = await client.automation_studio.get_projects()

    print(f"Total projects: {len(all_projects)}")
```

The library uses `asyncio.gather()` to fetch multiple pages concurrently for better performance.

## Async Best Practices

### Always Use Context Managers

```python
# Good - ensures proper cleanup
async with asyncplatform.client(**config) as client:
    result = await client.automation_studio.get_projects()

# Bad - manual cleanup required
client = asyncplatform.Client(**config)
result = await client.automation_studio.get_projects()
await client.cleanup()  # Easy to forget!
```

### Concurrent Operations

Use `asyncio.gather()` for concurrent operations:

```python
async with asyncplatform.client(**config) as client:
    # Fetch multiple resources concurrently
    projects, groups, accounts = await asyncio.gather(
        client.automation_studio.get_projects(),
        client.authorization.get_groups(),
        client.authorization.get_accounts()
    )
```

### Error Handling in Concurrent Operations

```python
import asyncio

async with asyncplatform.client(**config) as client:
    results = await asyncio.gather(
        client.automation_studio.get_projects(),
        client.authorization.get_groups(),
        return_exceptions=True  # Don't fail fast
    )

    for result in results:
        if isinstance(result, Exception):
            print(f"Error: {result}")
        else:
            print(f"Success: {len(result)} items")
```

## Next Steps

Now that you have the basics:

1. Explore the [Architecture Guide](architecture.md) to understand how AsyncPlatform works
2. Review [Examples](examples.md) for common use cases
3. Read the [Development Guide](development.md) to set up your development environment
4. Check the [Testing Guide](testing.md) to learn about writing tests

## Common Issues

### Import Errors

If you see `ModuleNotFoundError: No module named 'asyncplatform'`:

```bash
# Ensure you're in the correct environment
uv sync

# Or reinstall the package
uv add asyncplatform
```

### Connection Errors

If you can't connect to the platform:

1. Verify the hostname is correct
2. Check that the port is accessible
3. Ensure credentials are valid
4. Verify SSL certificates if using HTTPS

### Async Errors

If you see `RuntimeError: no running event loop`:

```python
# Don't use await at the module level
# Instead, wrap in an async function

async def main():
    async with asyncplatform.client(**config) as client:
        await client.automation_studio.get_projects()

# Run with asyncio.run()
asyncio.run(main())
```

## Additional Resources

- [Architecture Documentation](architecture.md)
- [API Examples](examples.md)
- [Testing Guide](testing.md)
- [Contributing Guidelines](contributing.md)

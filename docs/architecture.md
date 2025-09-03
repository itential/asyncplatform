# AsyncPlatform Architecture

This document provides a comprehensive overview of AsyncPlatform's architecture, design patterns, and core components.

## Table of Contents

- [Overview](#overview)
- [Design Principles](#design-principles)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Module Structure](#module-structure)

## Overview

AsyncPlatform is built on a layered architecture that separates concerns and promotes code reusability:

```
┌─────────────────────────────────────────┐
│         Application Layer               │  Examples, User Code
├─────────────────────────────────────────┤
│         Resource Layer                  │  High-level abstractions
├─────────────────────────────────────────┤
│         Service Layer                   │  API service implementations
├─────────────────────────────────────────┤
│         Client Layer                    │  Client, Context, Loaders
├─────────────────────────────────────────┤
│         Foundation Layer                │  HTTP, Logging, Exceptions
└─────────────────────────────────────────┘
```

## Design Principles

### 1. Async-First

Every API call is async by default, leveraging Python's `asyncio` for concurrent operations:

```python
# Multiple concurrent API calls
results = await asyncio.gather(
    client.automation_studio.get_projects(),
    client.authorization.get_groups(),
    client.operations_manager.find_automations()
)
```

### 2. Separation of Concerns

- **Services**: Handle direct API communication
- **Resources**: Provide high-level business logic
- **Models**: Define data structures
- **Client**: Manages lifecycle and service discovery

### 3. Plugin Architecture

Services and resources are discovered dynamically from their respective directories:

```
src/asyncplatform/
├── services/           # Auto-discovered services
│   ├── __init__.py
│   ├── automation_studio.py
│   ├── authorization.py
│   └── operations_manager.py
└── resources/          # Auto-discovered resources
    ├── __init__.py
    ├── projects.py
    └── automations.py
```

### 4. Fail-Fast with Clear Errors

All errors use custom exception classes with detailed messages:

```python
raise exceptions.NotFoundError(
    f"workflow id {workflow_id} not found"
)
```

## Core Components

### Client (`client.py`)

The main entry point for interacting with the platform.

```python
class Client:
    """Main client class for Itential Platform API."""

    def __init__(self, **kwargs):
        # Create shared context
        self.ctx = Context()

        # Load all services dynamically
        self._load_services()

    async def __aenter__(self):
        # Initialize platform connection
        self.ctx.client = ipsdk.platform_factory(want_async=True)
        await self.ctx.client.connect(**self.config)
        return self

    async def __aexit__(self, *args):
        # Cleanup resources
        await self.ctx.cleanup()
```

**Key Responsibilities:**
- Service discovery and instantiation
- Connection lifecycle management
- Resource loading on demand
- Configuration management

### Context (`context.py`)

Provides shared state between services:

```python
class Context:
    """Shared context for services."""

    def __init__(self):
        self.client = None  # ipsdk.AsyncPlatform instance

    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            await self.client.close()
```

**Key Responsibilities:**
- Holds the ipsdk client connection
- Provides cleanup mechanism
- Shared across all services

### Services (`services/`)

Services provide direct access to platform APIs.

#### ServiceBase (`services/__init__.py`)

All services inherit from `ServiceBase`:

```python
class ServiceBase:
    """Base class for all services."""

    def __init__(self, ctx: Context):
        self.ctx = ctx

    async def get(self, path, **kwargs):
        """GET request wrapper."""
        return await self._send_request("GET", path, **kwargs)

    async def post(self, path, **kwargs):
        """POST request wrapper."""
        return await self._send_request("POST", path, **kwargs)

    # ... other HTTP methods
```

**Features:**
- Automatic error handling
- Status code validation
- Consistent error messages
- HTTP method helpers

#### Example Service (`services/automation_studio.py`)

```python
class Service(ServiceBase):
    """Automation Studio service."""

    name = "automation_studio"

    async def get_projects(self):
        """Get all projects with automatic pagination."""
        params = {"limit": 100}
        res = await self.get("/automation-studio/projects", params=params)
        data = res.json()

        total = data["metadata"]["total"]
        if total <= 100:
            return data["data"]

        # Fetch remaining pages concurrently
        tasks = [...]
        results = await asyncio.gather(*tasks)
        return all_results
```

**Key Responsibilities:**
- API endpoint mapping
- Request/response handling
- Automatic pagination
- Data transformation

### Resources (`resources/`)

Resources provide high-level abstractions that combine multiple services.

#### ResourceBase (`resources/__init__.py`)

```python
class ResourceBase:
    """Base class for all resources."""

    def __init__(self, client: Client):
        self.client = client

    @property
    def studio(self):
        """Access Automation Studio service."""
        return self.client.automation_studio

    @property
    def authorization(self):
        """Access Authorization service."""
        return self.client.authorization
```

**Features:**
- Service access via properties
- Shared caching for groups/accounts
- High-level operation methods

#### Example Resource (`resources/projects.py`)

```python
class Resource(ResourceBase):
    """Projects resource."""

    name = "projects"

    async def importer(self, project, members=None):
        """Import project with member assignments."""
        # 1. Validate project doesn't exist
        await self._ensure_project_is_new(project["name"])

        # 2. Import project
        result = await self.studio.import_project(project)

        # 3. Add members if specified
        if members:
            await self._update_project_members(
                result["_id"], result, members
            )

        return result
```

**Key Responsibilities:**
- Complex workflows
- Cross-service operations
- Business logic
- Data validation

### Loader (`loader.py`)

Dynamic class loading with caching:

```python
class Loader:
    """Dynamic module loader with caching."""

    def __init__(self, path, class_name):
        self.path = path
        self.class_name = class_name
        self._cache = {}

    def __call__(self, name, *args, **kwargs):
        """Load and instantiate class."""
        if name not in self._cache:
            module = importlib.import_module(f"{self.path}.{name}")
            self._cache[name] = getattr(module, self.class_name)

        return self._cache[name](*args, **kwargs)
```

**Features:**
- Module caching
- Lazy loading
- Plugin discovery

## Data Flow

### Service Request Flow

```
User Code
    ↓
Client.service.method()
    ↓
ServiceBase._send_request()
    ↓
ipsdk.AsyncPlatform (HTTP)
    ↓
Itential Platform API
    ↓
Response Processing
    ↓
Return to User
```

### Resource Request Flow

```
User Code
    ↓
Client.resource("name").method()
    ↓
Resource._method_implementation()
    ↓
Multiple Service Calls
    ├→ Service A
    ├→ Service B
    └→ Service C
    ↓
Business Logic
    ↓
Return to User
```

## Design Patterns

### 1. Context Manager Pattern

Used for automatic resource cleanup:

```python
async with asyncplatform.client(**config) as client:
    # Resources automatically cleaned up on exit
    await client.automation_studio.get_projects()
```

### 2. Factory Pattern

Services and resources are created via factories:

```python
# Services loaded via factory
services_loader = Loader("asyncplatform.services", "Service")
service = services_loader("automation_studio", ctx)

# Resources loaded via factory
resources_loader = Loader("asyncplatform.resources", "Resource")
resource = resources_loader("projects", client)
```

### 3. Decorator Pattern

Used for cross-cutting concerns:

```python
@logging.trace
async def get_projects(self):
    """Automatically logs entry/exit with timing."""
    return await self.get("/automation-studio/projects")
```

### 4. Template Method Pattern

`ServiceBase` provides template for all services:

```python
class ServiceBase:
    async def _send_request(self, method, path, **kwargs):
        """Template method for all HTTP requests."""
        try:
            response = await self.ctx.client.request(...)
            self._validate_status(response, expected)
            return response
        except Exception as e:
            raise AsyncPlatformError(...) from e
```

### 5. Strategy Pattern

Different pagination strategies for different endpoints:

```python
# Simple pagination (total <= limit)
if total <= limit:
    return data["data"]

# Concurrent pagination (total > limit)
tasks = [fetch_page(i) for i in range(num_pages)]
results = await asyncio.gather(*tasks)
```

## Module Structure

### Foundation Modules

**`http.py`**: HTTP enumerations and response wrappers

```python
class HTTPMethod(IntEnum):
    GET = 1
    POST = 2
    # ...

class HTTPStatus(IntEnum):
    OK = 200
    CREATED = 201
    # ...
```

**`exceptions.py`**: Custom exception hierarchy

```python
class AsyncPlatformError(Exception):
    """Base exception."""

class NotFoundError(AsyncPlatformError):
    """Resource not found (404)."""

class SerializationError(AsyncPlatformError):
    """JSON parsing error."""
```

**`logging.py`**: Comprehensive logging system

```python
# Custom log levels
TRACE = 5    # Detailed tracing
FATAL = 90   # Fatal errors
NONE = 100   # Disable logging

# Sensitive data filtering
enable_sensitive_data_filtering()

# Function tracing decorator
@trace
async def my_function():
    pass
```

**`jsonutils.py`**: JSON utilities with error handling

```python
def loads(s: str) -> dict | list:
    """Parse JSON with custom error handling."""
    try:
        return json.loads(s)
    except json.JSONDecodeError as exc:
        raise SerializationError(...) from exc
```

### Model Modules

**`models/projects.py`**: Data models using dataclasses

```python
@dataclass(slots=True, kw_only=True, frozen=True)
class ProjectMember:
    """Project member model."""
    username: str | None = None
    name: str | None = None
    type: str | None = None
    role: Literal["owner", "editor", "operator", "viewer"] = "viewer"

    def asdict(self):
        """Convert to dict, excluding None values."""
        return {f.name: v for f in fields(self) if (v := getattr(self, f.name)) is not None}
```

## Concurrency Model

### Async/Await

All I/O operations use async/await:

```python
# Async function
async def get_projects(self):
    response = await self.ctx.client.get(...)
    return response.json()

# Calling code
projects = await service.get_projects()
```

### Concurrent Requests

Multiple requests in parallel:

```python
# Sequential
for skip in range(0, total, 100):
    page = await get_page(skip)  # Slow

# Concurrent
tasks = [get_page(skip) for skip in range(0, total, 100)]
pages = await asyncio.gather(*tasks)  # Fast
```

### Error Handling in Concurrent Operations

```python
results = await asyncio.gather(*tasks, return_exceptions=True)

for result in results:
    if isinstance(result, Exception):
        raise result  # Re-raise first exception
    all_data.extend(result)
```

## Extension Points

### Adding New Services

1. Create `services/my_service.py`
2. Define `Service` class inheriting from `ServiceBase`
3. Set `name` attribute
4. Implement methods using HTTP helpers

```python
class Service(ServiceBase):
    name = "my_service"

    async def my_method(self):
        return await self.get("/my-service/endpoint")
```

### Adding New Resources

1. Create `resources/my_resource.py`
2. Define `Resource` class inheriting from `ResourceBase`
3. Set `name` attribute
4. Implement high-level methods

```python
class Resource(ResourceBase):
    name = "my_resource"

    async def complex_operation(self):
        # Use multiple services
        data1 = await self.studio.get_projects()
        data2 = await self.authorization.get_groups()
        # Combine and process
        return result
```

### Adding Custom Models

1. Create model in `models/`
2. Use `@dataclass` with type hints
3. Implement helper methods as needed

```python
@dataclass(slots=True, frozen=True)
class MyModel:
    field1: str
    field2: int | None = None

    def asdict(self):
        return asdict(self)
```

## Performance Considerations

### Pagination Performance

- **Concurrent fetching**: Multiple pages fetched simultaneously
- **Optimal page size**: 100 items per page balances requests and data size
- **Early termination**: Stop if all data retrieved

### Connection Pooling

- ipsdk handles connection pooling internally
- Reuse client instance across requests
- Close connections properly via context manager

### Memory Usage

- Streaming not currently supported (all data loaded into memory)
- Consider pagination for very large datasets
- Use dataclasses with `slots=True` for memory efficiency

## Security Considerations

### Credential Handling

- Never log passwords or tokens
- Use sensitive data filtering in logging
- Credentials passed via config, not hardcoded

### SSL/TLS

- SSL verification enabled by default
- Can be disabled for dev/test environments
- Certificate validation via ipsdk

### Error Messages

- Don't include sensitive data in error messages
- Use generic messages for authentication failures
- Log details securely, return safe messages to users

## Testing Architecture

### Test Structure

```
tests/
└── unit/
    ├── test_client.py          # Client tests
    ├── test_services_*.py      # Service tests
    ├── test_resources_*.py     # Resource tests
    └── test_*.py               # Utility tests
```

### Mocking Strategy

- Mock ipsdk client for unit tests
- Mock service responses for resource tests
- Use `AsyncMock` for async functions
- Avoid external dependencies in tests

See [Testing Guide](testing.md) for details.

## Next Steps

- [Development Setup](development.md) - Set up your development environment
- [Testing Guide](testing.md) - Learn about the testing strategy
- [Contributing](contributing.md) - Guidelines for contributors
- [Examples](examples.md) - Practical usage examples

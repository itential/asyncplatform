# AsyncPlatform

An async Python client library for the Itential Platform REST API.

AsyncPlatform provides a high-level, asynchronous interface for interacting with Itential Automation Platform services. Built on top of [ipsdk](https://github.com/itential/ipsdk), it offers a plugin-based architecture with automatic service discovery and resource management.

## Features

- **Async/Await Support**: Built for modern Python with full asyncio support
- **High-Level Resources**: Complex operations simplified through resource abstractions
- **Type Hints**: Fully typed for better IDE support and type checking
- **Caching**: Built-in async-safe caching with TTL support
- **Context Management**: Automatic connection lifecycle management

## Requirements

- Python 3.10 or higher
- Itential Platform 2023.1 or higher

## Installation

```bash
pip install asyncplatform
```

## Quick Start

### Basic Usage

```python
import asyncplatform

async def main():
    cfg = {
        "host": "platform.example.com",
        "user": "admin@domain",
        "password": "your-password"
    }

    async with asyncplatform.client(**cfg) as client:
        # Access services directly
        projects = await client.automation_studio.get_projects()
        print(f"Found {len(projects)} projects")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Using Services

Services provide access to specific Itential Platform APIs:

```python
async with asyncplatform.client(**cfg) as client:
    # Get all projects
    projects = await client.automation_studio.get_projects()

    # Get specific project details
    project = await client.automation_studio.describe_project("project-id")

    # Get authorization groups
    groups = await client.authorization.get_groups()

    # Get user accounts
    accounts = await client.authorization.get_accounts()
```

### Using Resources

Resources provide high-level abstractions for complex operations:

```python
from asyncplatform.models.projects import ProjectMember

async with asyncplatform.client(**cfg) as client:
    # Get the projects resource
    projects = client.resource("projects")

    # Import a project with member assignments
    project_data = {
        "name": "My Project",
        "description": "Project description"
    }

    members = [
        ProjectMember(name="admin_group", type="group", role="owner"),
        ProjectMember(name="user@example.com", type="account", role="editor")
    ]

    result = await projects.importer(project_data, members=members)
    print(f"Imported project: {result['name']}")

    # Delete a project by name
    await projects.delete("My Project")
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/itential/asyncplatform.git
cd asyncplatform

# Install dependencies
uv sync
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/asyncplatform --cov-report=term

# Run specific test file
uv run pytest tests/unit/test_loader.py
```

### Code Quality

```bash
# Linting
uv run ruff check src/asyncplatform tests

# Type checking
uv run mypy src/asyncplatform

# Formatting
uv run ruff format src/asyncplatform tests
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, development workflow, and the process for submitting pull requests.

## Documentation

- [AGENTS.md](AGENTS.md) - Project overview and architecture for AI assistants
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide and contribution guidelines
- [Itential Platform Documentation](https://docs.itential.com/)

## Support

- Report bugs and feature requests via [GitHub Issues](https://github.com/itential/asyncplatform/issues)
- For questions about the Itential Platform, visit [Itential Documentation](https://docs.itential.com/)

## License

Copyright (c) 2025 Itential, Inc

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

See [LICENSE](LICENSE) for the full license text and [LICENSES.md](LICENSES.md) for third-party license information.

# AsyncPlatform

> Async Python client library for the Itential Platform REST API.

AsyncPlatform provides a high-level, asynchronous interface for the Itential Automation Platform. It wraps [ipsdk](https://github.com/itential/ipsdk) with automatic service discovery, resource abstractions, and connection lifecycle management.

## Requirements

- Python 3.10+
- Itential Platform 2023.1+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Installation

```bash
# with uv (recommended)
uv add asyncplatform

# with pip
pip install asyncplatform
```

## Quick Start

```python
import asyncio
import asyncplatform

async def main():
    cfg = {
        "host": "platform.example.com",
        "user": "admin@domain",
        "password": "your-password",
    }

    async with asyncplatform.client(**cfg) as client:
        projects = await client.automation_studio.get_projects()
        print(f"Found {len(projects)} projects")

asyncio.run(main())
```

## Usage

### Services

Services map directly to Itential Platform APIs and are available as attributes on the client:

```python
async with asyncplatform.client(**cfg) as client:
    # Automation Studio
    projects = await client.automation_studio.get_projects()
    project = await client.automation_studio.describe_project("project-id")

    # Authorization
    groups = await client.authorization.get_groups()
    accounts = await client.authorization.get_accounts()
```

Available services: `automation_studio`, `authorization`, `configuration_manager`,
`lifecycle_manager`, `operations_manager`, `help`.

### Resources

Resources combine multiple service calls into single high-level operations:

```python
from asyncplatform.models.projects import ProjectMember

async with asyncplatform.client(**cfg) as client:
    projects = client.resource("projects")

    members = [
        ProjectMember(name="admin_group", type="group", role="owner"),
        ProjectMember(name="user@example.com", type="account", role="editor"),
    ]

    result = await projects.importer(project_data, members=members)
    await projects.delete("My Project")
```

Available resources: `projects`, `automations`.

## Development

**Prerequisites**: Python 3.10+, [uv](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/itential/asyncplatform.git
cd asyncplatform
uv sync --group dev
```

```bash
make test        # run tests
make lint        # lint src/ and tests/
make coverage    # test with HTML coverage report
make security    # bandit security scan
make premerge    # full premerge checks (lint + test + security)
make tox         # test across Python 3.10–3.13
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and the [`docs/`](docs/) directory for architecture, testing patterns, and contribution guidelines.

## License

Copyright (c) 2025 Itential, Inc. GPL-3.0-or-later — see [LICENSE](LICENSE) and [NOTICE](NOTICE).

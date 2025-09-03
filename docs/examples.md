# Usage Examples

This guide provides practical examples of using AsyncPlatform for common tasks.

## Table of Contents

- [Basic Examples](#basic-examples)
- [Working with Projects](#working-with-projects)
- [Working with Automations](#working-with-automations)
- [Working with Authorization](#working-with-authorization)
- [Advanced Patterns](#advanced-patterns)
- [Error Handling](#error-handling)
- [Performance Optimization](#performance-optimization)

## Basic Examples

### Simple Connection

```python
import asyncio
import asyncplatform

async def main():
    config = {
        "host": "platform.example.com",
        "user": "admin@domain",
        "password": "password"
    }

    async with asyncplatform.client(**config) as client:
        # Your code here
        projects = await client.automation_studio.get_projects()
        print(f"Found {len(projects)} projects")

asyncio.run(main())
```

### Logging Configuration

```python
from asyncplatform import logging

# Set log level
logging.set_level(logging.INFO)

# Enable detailed tracing
logging.set_level(logging.TRACE)

# Enable sensitive data filtering
logging.enable_sensitive_data_filtering()

# Add custom pattern
logging.add_sensitive_data_pattern("secret_key", r"secret_key=\w+")
```

## Working with Projects

### List All Projects

```python
async with asyncplatform.client(**config) as client:
    # Get all projects (handles pagination automatically)
    projects = await client.automation_studio.get_projects()

    for project in projects:
        print(f"Project: {project['name']}")
        print(f"  ID: {project['_id']}")
        print(f"  Created: {project.get('createdAt', 'N/A')}")
```

### Get Project Details

```python
async with asyncplatform.client(**config) as client:
    # Get detailed information about a specific project
    project_id = "507f1f77bcf86cd799439011"
    project = await client.automation_studio.describe_project(project_id)

    if project:
        print(f"Project: {project['name']}")
        print(f"Description: {project.get('description', 'No description')}")
        print(f"Members: {len(project.get('members', []))}")
    else:
        print("Project not found")
```

### Find Projects by Name

```python
async with asyncplatform.client(**config) as client:
    # Search for projects by name
    projects = await client.automation_studio.find_projects(
        name="Production Automation"
    )

    if projects:
        print(f"Found {len(projects)} matching projects")
        for project in projects:
            print(f"  - {project['name']} ({project['_id']})")
    else:
        print("No projects found")
```

### Import a Project

```python
from pathlib import Path
import json

async with asyncplatform.client(**config) as client:
    # Load project data from file
    project_file = Path("project.json")
    project_data = json.loads(project_file.read_text())

    # Import the project
    result = await client.automation_studio.import_project(project_data)

    print(f"Imported project: {result['name']}")
    print(f"Project ID: {result['_id']}")
```

### Import Project with Members

```python
from asyncplatform.models.projects import ProjectMember

async with asyncplatform.client(**config) as client:
    # Load project data
    project_data = {
        "name": "New Automation Project",
        "description": "Automated network configuration"
    }

    # Define project members
    members = [
        ProjectMember(
            name="Administrators",
            type="group",
            role="owner"
        ),
        ProjectMember(
            username="john.doe@example.com",
            type="account",
            role="editor"
        ),
        ProjectMember(
            name="Operators",
            type="group",
            role="operator"
        )
    ]

    # Use projects resource for high-level operation
    projects_resource = client.resource("projects")
    result = await projects_resource.importer(
        project_data,
        members=members
    )

    print(f"Imported project: {result['name']}")
    print(f"Members added: {len(members)}")
```

### Update Project

```python
async with asyncplatform.client(**config) as client:
    project_id = "507f1f77bcf86cd799439011"

    # Update project fields
    updates = {
        "description": "Updated description",
        "tags": ["production", "networking"]
    }

    result = await client.automation_studio.patch_project(
        project_id,
        updates
    )

    print("Project updated successfully")
```

### Delete a Project

```python
async with asyncplatform.client(**config) as client:
    # Delete by ID
    project_id = "507f1f77bcf86cd799439011"
    result = await client.automation_studio.delete_project(project_id)

    print(f"Deleted project: {result}")

    # Or delete by name using resource
    projects_resource = client.resource("projects")
    result = await projects_resource.delete("Old Project")

    if result:
        print("Project deleted successfully")
    else:
        print("Project not found")
```

## Working with Automations

### List Automations

```python
async with asyncplatform.client(**config) as client:
    # Get all automations
    automations = await client.operations_manager.find_automations()

    for automation in automations:
        print(f"Automation: {automation['name']}")
        print(f"  Type: {automation.get('componentType')}")
        print(f"  Component: {automation.get('componentName')}")
```

### Find Specific Automation

```python
async with asyncplatform.client(**config) as client:
    # Find automation by name
    automations = await client.operations_manager.find_automations(
        name="Device Configuration"
    )

    if automations:
        automation = automations[0]
        print(f"Found automation: {automation['name']}")
        print(f"ID: {automation['_id']}")
    else:
        print("Automation not found")
```

### Import Automation

```python
async with asyncplatform.client(**config) as client:
    automation_data = {
        "name": "Network Backup",
        "description": "Daily network device backup",
        "componentType": "workflows",
        "componentName": "backup_workflow",
        "componentId": "wf123",
        "gbac": {
            "read": [],
            "write": []
        }
    }

    result = await client.operations_manager.import_automation(
        automation_data
    )

    print(f"Imported automation: {result['name']}")
    print(f"ID: {result['_id']}")
```

### Import Automation with GBAC

```python
async with asyncplatform.client(**config) as client:
    automation_data = {
        "name": "Critical Automation",
        "componentType": "workflows",
        "componentName": "critical_workflow",
        "componentId": "wf456",
        "gbac": {
            "read": [],
            "write": []
        }
    }

    # Use automations resource for GBAC management
    automations_resource = client.resource("automations")

    result = await automations_resource.importer(
        automation_data,
        write_groups=["Administrators"],
        read_groups=["Operators", "Viewers"],
        preserve_read_groups=False,
        preserve_write_groups=False
    )

    print(f"Imported automation: {result['name']}")
    print("GBAC groups configured")
```

### Delete Automation

```python
async with asyncplatform.client(**config) as client:
    automation_id = "507f1f77bcf86cd799439011"

    result = await client.operations_manager.delete_automation(
        automation_id
    )

    print("Automation deleted successfully")
```

## Working with Authorization

### List All Groups

```python
async with asyncplatform.client(**config) as client:
    # Get all authorization groups
    groups = await client.authorization.get_groups()

    for group in groups:
        print(f"Group: {group['name']}")
        print(f"  ID: {group['_id']}")
        print(f"  Description: {group.get('description', 'N/A')}")
```

### List All Accounts

```python
async with asyncplatform.client(**config) as client:
    # Get all user accounts
    accounts = await client.authorization.get_accounts()

    for account in accounts:
        print(f"User: {account['username']}")
        print(f"  ID: {account['_id']}")
        print(f"  Email: {account.get('email', 'N/A')}")
```

### Find Specific Group

```python
async with asyncplatform.client(**config) as client:
    groups = await client.authorization.get_groups()

    # Find group by name
    admin_group = next(
        (g for g in groups if g['name'] == 'Administrators'),
        None
    )

    if admin_group:
        print(f"Found group: {admin_group['name']}")
        print(f"ID: {admin_group['_id']}")
    else:
        print("Group not found")
```

## Advanced Patterns

### Concurrent Operations

```python
import asyncio

async with asyncplatform.client(**config) as client:
    # Fetch multiple resources concurrently
    projects, groups, accounts = await asyncio.gather(
        client.automation_studio.get_projects(),
        client.authorization.get_groups(),
        client.authorization.get_accounts()
    )

    print(f"Projects: {len(projects)}")
    print(f"Groups: {len(groups)}")
    print(f"Accounts: {len(accounts)}")
```

### Error Handling in Concurrent Operations

```python
import asyncio

async with asyncplatform.client(**config) as client:
    # Gather with exception handling
    results = await asyncio.gather(
        client.automation_studio.get_projects(),
        client.authorization.get_groups(),
        client.operations_manager.find_automations(),
        return_exceptions=True  # Don't fail fast
    )

    # Process results
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Operation {i} failed: {result}")
        else:
            print(f"Operation {i} succeeded: {len(result)} items")
```

### Batch Processing

```python
async with asyncplatform.client(**config) as client:
    # Get all projects
    projects = await client.automation_studio.get_projects()

    # Process in batches
    batch_size = 10
    for i in range(0, len(projects), batch_size):
        batch = projects[i:i + batch_size]

        # Process batch concurrently
        tasks = [
            process_project(client, project)
            for project in batch
        ]

        results = await asyncio.gather(*tasks)

        print(f"Processed batch {i//batch_size + 1}: {len(results)} projects")

async def process_project(client, project):
    """Process a single project."""
    details = await client.automation_studio.describe_project(
        project['_id']
    )
    # Do something with details
    return details
```

### Export and Import Workflow

```python
import json
from pathlib import Path

async def export_project(client, project_name, output_file):
    """Export a project to a file."""
    # Find project
    projects = await client.automation_studio.find_projects(
        name=project_name
    )

    if not projects:
        print(f"Project '{project_name}' not found")
        return

    project_id = projects[0]['_id']

    # Get full project details
    project = await client.automation_studio.describe_project(project_id)

    # Save to file
    output_path = Path(output_file)
    output_path.write_text(json.dumps(project, indent=2))

    print(f"Exported project to {output_file}")

async def import_project(client, input_file, new_name=None):
    """Import a project from a file."""
    # Load project data
    input_path = Path(input_file)
    project_data = json.loads(input_path.read_text())

    # Optionally rename
    if new_name:
        project_data['name'] = new_name

    # Import project
    result = await client.automation_studio.import_project(project_data)

    print(f"Imported project: {result['name']}")
    return result

# Usage
async with asyncplatform.client(**config) as client:
    # Export
    await export_project(client, "Production Workflow", "backup.json")

    # Import
    await import_project(client, "backup.json", "Restored Workflow")
```

### Caching with Resources

```python
async with asyncplatform.client(**config) as client:
    # Resources cache groups and accounts automatically
    projects_resource = client.resource("projects")

    # First call fetches groups from API
    groups = await projects_resource.get_groups()
    print(f"Fetched {len(groups)} groups")

    # Second call uses cache
    groups = await projects_resource.get_groups()
    print(f"Used cached {len(groups)} groups")
```

## Error Handling

### Basic Error Handling

```python
from asyncplatform import exceptions

async with asyncplatform.client(**config) as client:
    try:
        project = await client.automation_studio.describe_project(
            "invalid_id"
        )
    except exceptions.NotFoundError as e:
        print(f"Project not found: {e}")
    except exceptions.AsyncPlatformError as e:
        print(f"Platform error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

### Graceful Degradation

```python
async with asyncplatform.client(**config) as client:
    # Try to get projects, fall back to empty list
    try:
        projects = await client.automation_studio.get_projects()
    except exceptions.AsyncPlatformError as e:
        logging.warning(f"Failed to fetch projects: {e}")
        projects = []

    print(f"Processing {len(projects)} projects")
```

### Retry Logic

```python
import asyncio
from asyncplatform import exceptions

async def retry_operation(func, max_retries=3, delay=1):
    """Retry an async operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await func()
        except exceptions.AsyncPlatformError as e:
            if attempt == max_retries - 1:
                raise

            wait_time = delay * (2 ** attempt)
            logging.warning(
                f"Attempt {attempt + 1} failed: {e}. "
                f"Retrying in {wait_time}s..."
            )
            await asyncio.sleep(wait_time)

# Usage
async with asyncplatform.client(**config) as client:
    projects = await retry_operation(
        lambda: client.automation_studio.get_projects()
    )
```

## Performance Optimization

### Minimize API Calls

```python
async with asyncplatform.client(**config) as client:
    # Bad - multiple API calls
    for project_id in project_ids:
        project = await client.automation_studio.describe_project(
            project_id
        )
        process(project)

    # Good - fetch all at once, then process
    projects = await client.automation_studio.get_projects()
    projects_by_id = {p['_id']: p for p in projects}

    for project_id in project_ids:
        if project_id in projects_by_id:
            process(projects_by_id[project_id])
```

### Use Concurrent Requests

```python
import asyncio

async with asyncplatform.client(**config) as client:
    # Bad - sequential
    projects = await client.automation_studio.get_projects()
    groups = await client.authorization.get_groups()
    accounts = await client.authorization.get_accounts()

    # Good - concurrent
    projects, groups, accounts = await asyncio.gather(
        client.automation_studio.get_projects(),
        client.authorization.get_groups(),
        client.authorization.get_accounts()
    )
```

### Efficient Filtering

```python
async with asyncplatform.client(**config) as client:
    # Get all projects once
    all_projects = await client.automation_studio.get_projects()

    # Filter in memory (fast)
    production_projects = [
        p for p in all_projects
        if 'production' in p['name'].lower()
    ]

    active_projects = [
        p for p in all_projects
        if p.get('status') == 'active'
    ]
```

## Complete Example Script

```python
#!/usr/bin/env python
"""
Example script demonstrating AsyncPlatform usage.

This script:
1. Connects to the platform
2. Lists all projects
3. Imports a new project with members
4. Verifies the import
5. Cleans up
"""

import asyncio
import json
from pathlib import Path

import asyncplatform
from asyncplatform import logging
from asyncplatform.models.projects import ProjectMember

# Configuration
CONFIG = {
    "host": "platform.example.com",
    "user": "admin@domain",
    "password": "password"
}

async def main():
    """Main function."""
    # Configure logging
    logging.set_level(logging.INFO)

    # Connect to platform
    async with asyncplatform.client(**CONFIG) as client:
        # List existing projects
        print("Fetching projects...")
        projects = await client.automation_studio.get_projects()
        print(f"Found {len(projects)} existing projects")

        # Load project data
        project_file = Path("project.json")
        if not project_file.exists():
            print(f"Error: {project_file} not found")
            return

        project_data = json.loads(project_file.read_text())

        # Define members
        members = [
            ProjectMember(name="Administrators", type="group", role="owner"),
            ProjectMember(username="admin@domain", type="account", role="editor")
        ]

        # Import project
        print(f"Importing project: {project_data['name']}")
        projects_resource = client.resource("projects")

        try:
            result = await projects_resource.importer(
                project_data,
                members=members
            )

            print(f"✓ Successfully imported project: {result['name']}")
            print(f"  Project ID: {result['_id']}")

            # Verify
            projects = await client.automation_studio.get_projects()
            print(f"✓ Total projects after import: {len(projects)}")

        except asyncplatform.exceptions.AsyncPlatformError as e:
            print(f"✗ Import failed: {e}")
            return

if __name__ == "__main__":
    asyncio.run(main())
```

## Additional Resources

- [Getting Started Guide](getting-started.md) - Installation and basics
- [Architecture Documentation](architecture.md) - System design
- [Development Guide](development.md) - Development setup
- [Testing Guide](testing.md) - Writing tests
- [Contributing Guidelines](contributing.md) - How to contribute

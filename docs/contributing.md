# Contributing to AsyncPlatform

Thank you for your interest in contributing to AsyncPlatform! This guide will help you contribute effectively.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Code Style](#code-style)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Review Guidelines](#review-guidelines)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Prioritize project success over individual preferences
- Maintain professional communication

### Our Responsibilities

Maintainers are responsible for:

- Clarifying standards of acceptable behavior
- Taking appropriate action for unacceptable behavior
- Maintaining project quality and consistency

## Getting Started

### Prerequisites

Before contributing, ensure you have:

1. Python 3.10 or higher
2. uv package manager installed
3. Git configured with your name and email
4. Familiarity with async Python and pytest

### Initial Setup

```bash
# Fork and clone the repository
git clone <your-fork-url>
cd asyncplatform

# Add upstream remote
git remote add upstream <original-repo-url>

# Install dependencies
uv sync --group dev

# Verify setup
make test
```

## Development Process

### 1. Find or Create an Issue

- Check existing issues before starting work
- Create an issue for new features or bugs
- Discuss approach before implementing large changes
- Get maintainer approval for significant changes

### 2. Create a Branch

```bash
# Update devel branch
git checkout devel
git pull upstream devel

# Create feature branch
git checkout -b feature/description-of-change

# Or for bug fixes
git checkout -b fix/description-of-bug
```

### Branch Naming Conventions

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `test/` - Test improvements
- `refactor/` - Code refactoring

### 3. Make Changes

Follow these guidelines:

- Write clean, readable code
- Follow existing code style
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 4. Test Your Changes

```bash
# Run all tests
make test

# Run tests with coverage
make coverage

# Run linting
make lint

# Run security checks
make security

# Run everything
make premerge
```

### 5. Commit Your Changes

```bash
# Stage files
git add <files>

# Create commit with descriptive message
git commit

# Follow commit message format (see below)
```

### 6. Push and Create PR

```bash
# Push branch
git push origin feature/my-feature

# Create pull request
gh pr create --title "Add feature X" --body "Description"
```

## Code Style

### Python Style Guide

Follow these conventions from CLAUDE.md:

#### General

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces (never tabs)
- **Quotes**: Double quotes for strings
- **Blank lines**: 2 between top-level functions/classes, 1 between methods

#### Type Hints

Always use modern type hints:

```python
# Use Python 3.10+ syntax
def process(data: dict[str, Any]) -> list[str]:
    pass

# Not typing module versions
from typing import Dict, Any, List  # Don't do this
def process(data: Dict[str, Any]) -> List[str]:  # Don't do this
    pass
```

Use union syntax:

```python
# Good
def get_value(key: str) -> str | None:
    pass

# Bad
from typing import Optional
def get_value(key: str) -> Optional[str]:
    pass
```

#### Imports

Organize imports:

```python
# 1. Future imports
from __future__ import annotations

# 2. Standard library (alphabetical)
import asyncio
import json
from pathlib import Path
from typing import TYPE_CHECKING

# 3. Third-party (alphabetical)
import ipsdk

# 4. Local imports
from . import exceptions
from . import logging

# 5. TYPE_CHECKING imports
if TYPE_CHECKING:
    from collections.abc import Mapping
```

#### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief one-line description.

    Longer description explaining what the function does,
    any important details, and usage examples if helpful.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of the return value

    Raises:
        ValueError: When param2 is negative
        AsyncPlatformError: When API call fails
    """
    pass
```

**Don't include**:
- Type information in docstrings (use type hints)
- None/empty sections
- Obvious information

#### File Headers

All Python files must include:

```python
# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
```

### Async Best Practices

#### Use async/await

```python
# Good
async def get_data(self):
    result = await self.ctx.client.get(...)
    return result.json()

# Bad - blocking
def get_data(self):
    result = requests.get(...)  # Blocking!
    return result.json()
```

#### Use asyncio.gather for concurrency

```python
# Good - concurrent
results = await asyncio.gather(
    self.get_projects(),
    self.get_groups(),
    self.get_accounts()
)

# Bad - sequential
projects = await self.get_projects()
groups = await self.get_groups()
accounts = await self.get_accounts()
```

#### Handle exceptions in gather

```python
# With exception handling
results = await asyncio.gather(
    *tasks,
    return_exceptions=True
)

for result in results:
    if isinstance(result, Exception):
        raise result
    process(result)
```

### Error Handling

#### Use custom exceptions

```python
# Good
if not found:
    raise exceptions.NotFoundError(f"Project {name} not found")

# Bad
if not found:
    raise Exception("Not found")  # Too generic
```

#### Chain exceptions

```python
# Good - preserves context
try:
    data = json.loads(string)
except json.JSONDecodeError as exc:
    raise exceptions.SerializationError(...) from exc

# Bad - loses context
try:
    data = json.loads(string)
except json.JSONDecodeError:
    raise exceptions.SerializationError(...)  # No 'from exc'
```

#### Don't suppress exceptions unnecessarily

```python
# Good - let errors propagate
async def get_data(self):
    return await self.client.get(...)

# Bad - hiding errors
async def get_data(self):
    try:
        return await self.client.get(...)
    except Exception:
        return None  # What went wrong?
```

### Code Organization

#### Keep functions focused

```python
# Good - single responsibility
async def get_projects(self):
    """Get all projects."""
    return await self._fetch_with_pagination("/projects")

async def _fetch_with_pagination(self, path):
    """Fetch data with automatic pagination."""
    # Pagination logic here
    pass

# Bad - doing too much
async def get_projects(self):
    """Get all projects."""
    # Mix of business logic and pagination
    # Hard to test and reuse
    pass
```

#### Use early returns

```python
# Good
async def process(self, data):
    if not data:
        return []

    if len(data) == 1:
        return data

    return self._process_multiple(data)

# Bad - nested
async def process(self, data):
    if data:
        if len(data) > 1:
            return self._process_multiple(data)
        else:
            return data
    else:
        return []
```

## Testing Requirements

### Required Tests

All new code must include tests:

1. **Services**: Test all public methods
2. **Resources**: Test all public methods
3. **Utilities**: Test all functions
4. **Error handling**: Test all error paths

### Type Checking

All code must pass mypy type checking:

```bash
# Check source code
uv run mypy src/asyncplatform

# Check tests (uses relaxed configuration from pyproject.toml)
uv run mypy tests
```

### Test Quality

```python
# Good test
@pytest.mark.asyncio
async def test_get_projects_returns_empty_list_when_no_projects(self):
    """Test get_projects returns empty list when no projects exist."""
    ctx = context.Context()
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "metadata": {"total": 0},
        "data": []
    }
    mock_client.get = AsyncMock(return_value=mock_response)
    ctx.client = mock_client

    service = Service(ctx)
    result = await service.get_projects()

    assert isinstance(result, list)
    assert len(result) == 0
```

See [Testing Guide](testing.md) for details.

## Documentation

### When to Update Documentation

Update documentation when:

- Adding new features
- Changing existing behavior
- Adding new modules
- Changing APIs
- Fixing bugs (if docs were misleading)

### Documentation Locations

- **Docstrings**: Inline code documentation
- **docs/**: User-facing documentation
- **CLAUDE.md**: Project guidelines for AI assistants
- **README.md**: Project overview
- **examples/**: Usage examples

### Documentation Style

- Use clear, concise language
- Include code examples
- Explain "why" not just "what"
- Keep documentation up-to-date with code

## Pull Request Process

### Before Submitting

Checklist:

- [ ] Code follows style guidelines
- [ ] All tests pass (`make test`)
- [ ] Coverage maintained or improved (`make coverage`)
- [ ] Type checking passes (`uv run mypy tests`)
- [ ] Linting passes (`make lint`)
- [ ] Security checks pass (`make security`)
- [ ] Documentation updated
- [ ] Commit messages follow format
- [ ] Branch is up-to-date with devel

### PR Title Format

Use conventional commit format:

```
<type>: <description>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation only
- test: Testing improvements
- refactor: Code refactoring
- perf: Performance improvement
- style: Code style changes
- chore: Maintenance tasks
```

Examples:
- `feat: add operations manager service`
- `fix: handle pagination edge case`
- `docs: update architecture guide`
- `test: improve coverage for client module`

### PR Description Template

```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- Change 1
- Change 2
- Change 3

## Testing
How was this tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All checks passing
- [ ] Ready for review
```

### Commit Message Format

```
<type>: <short description>

<longer description if needed>

- Bullet point 1
- Bullet point 2

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Do not include**:
- Standard footer (per user preferences)
- Issue numbers in title (put in description)

## Review Guidelines

### For Contributors

When your PR is under review:

- **Respond promptly** to reviewer feedback
- **Be open** to suggestions
- **Explain** your approach if asked
- **Update** PR based on feedback
- **Ask questions** if anything is unclear

### For Reviewers

When reviewing PRs:

- **Be constructive** and respectful
- **Explain** why changes are needed
- **Approve** when ready, don't nitpick
- **Test** the changes if possible
- **Check** test coverage and documentation

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are comprehensive
- [ ] Documentation is clear
- [ ] No security issues
- [ ] Performance is acceptable
- [ ] Error handling is appropriate
- [ ] API is intuitive

## Common Pitfalls

### Don't

- ❌ Push directly to devel or main
- ❌ Commit without running tests
- ❌ Submit PRs with failing tests
- ❌ Include unrelated changes
- ❌ Ignore review feedback
- ❌ Use `git commit --no-verify` (skips hooks)
- ❌ Commit secrets or credentials
- ❌ Make breaking changes without discussion

### Do

- ✅ Create feature branches
- ✅ Run `make premerge` before submitting
- ✅ Write comprehensive tests
- ✅ Update documentation
- ✅ Respond to reviews
- ✅ Ask questions if unsure
- ✅ Keep PRs focused and small
- ✅ Follow existing patterns

## Getting Help

If you need help:

1. Check existing documentation
2. Review similar code in the project
3. Ask questions in PR comments
4. Open a discussion issue

## Recognition

Contributors will be:

- Listed in commit history
- Credited in release notes (if significant contribution)
- Mentioned in project documentation (if appropriate)

## License

By contributing, you agree that your contributions will be licensed under the GPL-3.0-or-later license.

---

Thank you for contributing to AsyncPlatform! Your contributions help make this project better for everyone.

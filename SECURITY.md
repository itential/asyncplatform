# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in the asyncplatform library, please report it responsibly:

1. **Do not** create a public GitHub issue
2. Email security details to: **opensource@itential.com**
3. Include steps to reproduce the vulnerability
4. Provide any relevant technical details
5. Include the affected version(s)

We will respond to security reports within 48 hours and provide regular updates on our progress.

### What to Include in Your Report

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Affected version(s)
- Any proof-of-concept code (if applicable)
- Suggested fixes (if you have any)

## Security Best Practices

### Authentication and Credentials

- **Never hardcode credentials** in your source code
- Use environment variables or secure credential management systems
- Rotate authentication tokens regularly
- Use OAuth with client credentials flow when available
- Store credentials with appropriate file permissions (600 or restrictive)

```python
# Good: Use environment variables
import os
import asyncplatform

async def main():
    async with asyncplatform.client(
        host=os.getenv("ITENTIAL_HOST"),
        user=os.getenv("ITENTIAL_USER"),
        password=os.getenv("ITENTIAL_PASSWORD")
    ) as client:
        # Use client here
        pass

# Bad: Hardcoded credentials
async def bad_example():
    async with asyncplatform.client(
        host="production.example.com",
        user="admin",
        password="secret123"  # Never do this!
    ) as client:
        pass
```

### TLS and Certificate Verification

- **Always use HTTPS** in production environments
- **Never disable certificate verification** unless absolutely necessary for development
- Use proper CA certificates and validate certificate chains
- Configure appropriate TLS versions (1.2+)

```python
# Good: Secure TLS configuration
async with asyncplatform.client(
    host="itential.example.com",
    user=user,
    password=password,
    use_tls=True,      # Use HTTPS (default: True)
    verify=True,       # Verify certificates (default: True)
    timeout=30
) as client:
    # Use client here
    pass

# Bad: Disabled certificate verification (only for development/testing)
async with asyncplatform.client(
    host="itential.example.com",
    user=user,
    password=password,
    verify=False  # Only for development - never in production!
) as client:
    pass
```

### Network Security

- Use network segmentation and firewalls to restrict access
- Implement proper timeout values to prevent hanging connections
- Use connection pooling appropriately
- Monitor and log API access patterns

### Error Handling and Information Disclosure

- Handle exceptions properly without exposing sensitive information
- Sanitize error messages before logging or displaying
- Use structured logging with appropriate log levels
- Avoid logging sensitive data (credentials, tokens, personal information)

```python
import logging
from asyncplatform import exceptions

# Configure logging securely
logging.basicConfig(level=logging.INFO)  # Avoid DEBUG in production

async def secure_api_call():
    try:
        async with asyncplatform.client(
            host=host,
            user=user,
            password=password
        ) as client:
            # Make API calls
            result = await client.adapters.getall()
            return result
    except exceptions.AsyncPlatformError as e:
        # Good: Log error without sensitive details
        logging.error("Platform API request failed: %s", str(e))
        raise
    except Exception as e:
        # Bad: Don't log full client configuration or credentials
        # logging.error("Request failed with config: %s", client.__dict__)
        logging.error("Unexpected error: %s", type(e).__name__)
        raise
```

### Input Validation and Sanitization

- Validate all input parameters
- Sanitize data before sending to APIs
- Use proper data structures and avoid string concatenation
- Implement rate limiting and retry logic for API calls

```python
# Good: Validate input parameters
async def get_adapter_data(adapter_name: str):
    if not isinstance(adapter_name, str) or not adapter_name:
        raise ValueError("Invalid adapter_name")

    # Sanitize adapter_name
    safe_name = adapter_name.strip()

    async with asyncplatform.client(
        host=host,
        user=user,
        password=password
    ) as client:
        # Use the API safely
        adapters = await client.adapters.getall()
        return [a for a in adapters if a["name"] == safe_name]

# Bad: No validation
async def bad_get_adapter(adapter_name):
    async with asyncplatform.client(host=host, user=user, password=password) as client:
        # Unchecked input could cause issues
        return await client.adapters.getall()
```

### Dependency Management

- Regularly update dependencies to patch security vulnerabilities
- Use dependency scanning tools in CI/CD pipeline
- Pin dependency versions in production
- Monitor security advisories for ipsdk and other dependencies

```bash
# Keep dependencies updated
uv sync --upgrade

# Check for outdated packages
uv pip list --outdated

# Update the lock file
uv lock --upgrade
```

### Development Security

- Use code review processes for all changes
- Run linting and tests before committing
- Implement static analysis tools (ruff)
- Follow secure coding practices

```bash
# Run linting
make lint

# Run tests
make test

# Run full premerge checks
make premerge

# Run with coverage
make coverage
```

### Async Security Considerations

When using async connections:

- Always use async context managers for proper resource cleanup
- Set appropriate timeout values for async operations
- Handle async exceptions properly
- Avoid blocking the event loop with synchronous operations
- Use asyncio.gather() with proper error handling for concurrent operations

```python
import asyncio
import asyncplatform

# Good: Proper async resource management
async def secure_async_call():
    async with asyncplatform.client(
        host=host,
        user=user,
        password=password,
        timeout=30  # Set reasonable timeout
    ) as client:
        try:
            # Properly await async operations
            adapters = await client.adapters.getall()
            return adapters
        except asyncio.TimeoutError:
            # Handle timeout appropriately
            logging.error("Operation timed out")
            raise
        except Exception as e:
            # Handle other errors
            logging.error("Operation failed: %s", str(e))
            raise

# Good: Multiple concurrent operations with error handling
async def concurrent_operations():
    async with asyncplatform.client(
        host=host,
        user=user,
        password=password
    ) as client:
        try:
            # Run multiple operations concurrently
            results = await asyncio.gather(
                client.adapters.getall(),
                return_exceptions=True  # Handle errors individually
            )
            return results
        except Exception as e:
            logging.error("Concurrent operations failed: %s", str(e))
            raise
```

### Production Deployment

- Use secrets management systems (Kubernetes secrets, AWS Secrets Manager, etc.)
- Implement proper monitoring and alerting
- Use least-privilege access principles
- Regularly audit access logs and API usage
- Implement circuit breakers and retry mechanisms with backoff

### Code Quality and Security

Our development process includes quality checks:

- **Ruff**: Comprehensive linting including security-focused rules
- **Pytest**: Comprehensive unit test coverage
- **Type hints**: Static type checking for better code safety
- **Code review**: All changes reviewed before merging

## Security Testing

When testing the asyncplatform library:

- Use test credentials and isolated test environments
- Never use production credentials in tests
- Implement security-focused unit tests
- Test authentication failure scenarios
- Validate TLS certificate handling
- Test timeout and error handling
- Verify proper resource cleanup

```python
# Example security test
import pytest
import asyncplatform

@pytest.mark.asyncio
async def test_invalid_credentials():
    """Test that invalid credentials raise appropriate errors."""
    with pytest.raises(Exception):
        async with asyncplatform.client(
            host="test.example.com",
            user="invalid",
            password="invalid"
        ) as client:
            await client.adapters.getall()

@pytest.mark.asyncio
async def test_timeout_handling():
    """Test that timeouts are properly handled."""
    async with asyncplatform.client(
        host="test.example.com",
        user=user,
        password=password,
        timeout=1  # Very short timeout
    ) as client:
        # Should handle timeout gracefully
        pass
```

## Compliance and Standards

The asyncplatform library follows security best practices including:

- **Secure defaults**: TLS verification enabled, appropriate timeouts
- **Principle of least privilege**: Minimal required permissions
- **Defense in depth**: Multiple layers of security controls
- **Input validation**: Proper validation and sanitization
- **Secure error handling**: No sensitive data in error messages
- **Resource cleanup**: Proper context manager usage ensures cleanup

## Additional Resources

- [Itential Platform Documentation](https://docs.itential.com)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [asyncio Security Considerations](https://docs.python.org/3/library/asyncio-dev.html)

## Changelog

### Version 0.1.x
- Initial security policy established
- Secure defaults implemented
- Async context manager support for proper resource cleanup

# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import Path
from typing import Any

import ipsdk

from asyncplatform.loader import resources_loader
from asyncplatform.loader import services_loader

from . import context
from . import logging


class Client:
    """Main client for interacting with the Itential Platform API.

    The Client provides access to all platform services through a plugin-based
    architecture. Services are automatically loaded from the services directory
    and made available as attributes on the client instance.

    Supports async context manager protocol for proper resource cleanup.

    Example:
        async with asyncplatform.client(host="platform.example.com") as client:
            projects = await client.automation_studio.get_projects()
    """

    def __init__(
        self,
        *,
        host: str | None = None,
        port: int | None = None,
        use_tls: bool | None = None,
        verify: bool | None = None,
        user: str | None = None,
        password: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """Initialize the Client with platform connection parameters.

        Creates a new asyncplatform Client instance with the specified
        configuration for connecting to the Itential Platform.

        Args:
            host: Platform hostname (default: 'localhost')
            port: Platform port (default: 0)
            use_tls: Use TLS/HTTPS (default: True)
            verify: Verify SSL certificates (default: True)
            user: Username for authentication (default: 'admin')
            password: Password for authentication (default: 'admin')
            client_id: OAuth client ID (optional)
            client_secret: OAuth client secret (optional)
            timeout: Request timeout in seconds (default: 30)
        """
        self._context: context.Context | None = None

        self.__init_services__(
            host=host,
            port=port,
            use_tls=use_tls,
            verify=verify,
            user=user,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
            timeout=timeout,
        )

    async def __aenter__(self) -> Client:
        """Async context manager entry.

        Returns the client instance for use in async with statements.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> None:
        """Async context manager exit with proper resource cleanup.

        This method ensures all resources are properly cleaned up when
        the client exits the async context manager scope.
        """
        if self._context:
            await self._context.cleanup()

    def __init_services__(
        self,
        *,
        host: str | None = None,
        port: int | None = None,
        use_tls: bool | None = None,
        verify: bool | None = None,
        user: str | None = None,
        password: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """Initialize services by loading service modules and creating platform client.

        This method loads all service modules from the services directory and
        creates an ipsdk platform client with the provided configuration.

        Args:
            host: Platform hostname (default: 'localhost')
            port: Platform port (default: 0)
            use_tls: Use TLS/HTTPS (default: True)
            verify: Verify SSL certificates (default: True)
            user: Username for authentication (default: 'admin')
            password: Password for authentication (default: 'admin')
            client_id: OAuth client ID (optional)
            client_secret: OAuth client secret (optional)
            timeout: Request timeout in seconds (default: 30)
        """
        # Build kwargs dict and filter out None values
        kwargs = {
            "host": host,
            "port": port,
            "use_tls": use_tls,
            "verify": verify,
            "user": user,
            "password": password,
            "client_id": client_id,
            "client_secret": client_secret,
            "timeout": timeout,
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        path = Path(__file__).parent / "services"

        ctx = context.Context()
        ctx.client = ipsdk.platform_factory(want_async=True, **kwargs)

        # Store context reference for cleanup
        self._context = ctx

        # Get a list of all service files in the directory
        for f in path.glob("*.py"):
            if not f.name.startswith("_"):
                setattr(self, f.stem, services_loader.get(f.stem, ctx))

    @logging.trace
    def resource(self, name: str) -> Any:
        """Get a resource instance by name.

        Resources provide high-level abstractions that combine multiple
        services to perform complex operations. They are loaded dynamically
        from the resources directory.

        Args:
            name: The name of the resource to load (e.g., "projects")

        Raises:
            AsyncPlatformError: If the resource cannot be loaded or
                the Resource class is not found in the module
        """
        return resources_loader.get(name, self)

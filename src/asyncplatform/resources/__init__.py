# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Base resource classes for Itential Platform API resources.

This module provides the base classes for all resource implementations
in the asyncplatform library. Resources are high-level abstractions that
combine multiple API services to provide domain-specific functionality.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from asyncplatform import logging

if TYPE_CHECKING:
    from asyncplatform.client import Client


class ResourceBase:
    """Base class for all high-level resource abstractions.

    ResourceBase provides common functionality for all resource implementations,
    including access to services and shared caching mechanisms. Resources combine
    multiple service operations to provide high-level domain-specific functionality.

    Attributes:
        name: Resource identifier for logging and identification
        client: The AsyncPlatform client instance providing API access
        _groups_cache: Optional cached dictionary of authorization groups
        _accounts_cache: Optional cached dictionary of user accounts
    """

    name: str | None = None

    def __init__(self, client: Client) -> None:
        """Initialize the resource base with a client instance.

        Args:
            client: The AsyncPlatform client instance providing API access
        """
        self.client = client

        self._groups_cache: dict[str, dict[str, Any]] | None = None
        self._accounts_cache: dict[str, dict[str, Any]] | None = None

    @property
    def studio(self) -> Any:
        """Get the Automation Studio service instance."""
        return self.client.automation_studio

    @property
    def authorization(self) -> Any:
        """Get the Authorization service instance."""
        return self.client.authorization

    @property
    def operations_manager(self) -> Any:
        """Get the Operations Manager service instance."""
        return self.client.operations_manager

    @logging.trace
    async def get_groups(self) -> dict[str, dict[str, Any]]:
        """Retrieve and cache all authorization groups from the platform.

        Fetches all groups and creates a name-to-group mapping for efficient
        lookup. Results are cached to minimize API calls during member assignment.

        Raises:
            HTTPError: If the API request to retrieve groups fails
        """
        if self._groups_cache is None:
            res = await self.authorization.get_groups()
            self._groups_cache = {d["name"]: d for d in res}
        return self._groups_cache

    @logging.trace
    async def get_accounts(self) -> dict[str, dict[str, Any]]:
        """Retrieve and cache all user accounts from the platform.

        Fetches all user accounts and creates a username-to-account mapping for
        efficient lookup. Results are cached to minimize API calls during member
        assignment.

        Raises:
            HTTPError: If the API request to retrieve accounts fails
        """
        if self._accounts_cache is None:
            res = await self.authorization.get_accounts()
            self._accounts_cache = {d["username"]: d for d in res}
        return self._accounts_cache

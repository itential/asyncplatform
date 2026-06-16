# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Integration resource for managing Itential Platform integration instances.

This module provides the Resource class for high-level integration instance
management operations including creating instances and deleting instances by name.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from asyncplatform import logging
from asyncplatform.resources import ResourceBase

if TYPE_CHECKING:
    from collections.abc import Mapping


class Resource(ResourceBase):
    """Resource class for managing integration instances.

    Provides high-level lifecycle operations for integration instances, wrapping
    the integrations service with import and delete convenience methods.

    Attributes:
        integrations: Property that returns the Integrations service instance
    """

    name: str = "integrations"

    @logging.trace
    async def importer(
        self,
        *,
        name: str,
        type: str,
        properties: Mapping[str, Any],
        virtual: bool | None = None,
        model: str | None = None,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        """Create an integration instance, optionally replacing an existing one.

        Creates an integration instance with the given configuration. By default,
        raises an error if an instance with the same name already exists. Set
        overwrite=True to delete the existing instance before creating the new one.

        Args:
            name: Name for the integration instance
            type: The integration adapter type
            properties: Configuration properties for the integration
            virtual: Whether to create a virtual integration
            model: Optional integration model name to associate with the instance
            overwrite: If True, deletes an existing instance with the same name
                before creating. If False (default), raises an error if the
                instance already exists

        Returns:
            A dictionary containing the created integration instance data

        Raises:
            AsyncPlatformError: If overwrite is False and an instance with the
                same name already exists, or if any API request fails
        """
        if overwrite:
            existing = await self.integrations.find_integrations(name=name)
            if existing:
                await self.integrations.delete_integration(name)
                logging.info(f"Deleted existing integration instance: {name}")

        result = await self.integrations.create_integration(
            name=name,
            type=type,
            properties=properties,
            virtual=virtual,
            model=model,
        )

        logging.info(f"Successfully created integration instance: {name}")

        return result

    @logging.trace
    async def delete(self, name: str) -> dict[str, Any]:
        """Delete an integration instance by name.

        Searches for an integration instance by name and deletes it if found.
        Returns an empty dictionary if no matching instance exists.

        Args:
            name: The name of the integration instance to delete

        Returns:
            A dictionary containing the deletion result, or an empty dictionary
            if no instance with the specified name was found

        Raises:
            AsyncPlatformError: If the delete operation fails
        """
        existing = await self.integrations.find_integrations(name=name)
        if not existing:
            return {}

        return await self.integrations.delete_integration(name)

# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Configuration Manager resource for managing Itential Platform Golden Config trees.

This module provides the Resource class for high-level Configuration Manager
operations including exporting and importing Golden Config trees.
"""

from __future__ import annotations

import copy

from typing import Any

from asyncplatform import exceptions
from asyncplatform import logging
from asyncplatform.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing Configuration Manager Golden Config trees.

    This resource provides high-level operations for Configuration Manager
    golden config management including exporting a golden config tree by ID
    and importing one or more golden config trees into the platform.

    Attributes:
        configuration_manager: Property that returns the Configuration Manager
            service instance
    """

    name: str = "configuration_manager"

    async def check_if_golden_config_exists(self, name: str) -> bool:
        """Check if a Golden Config tree with the given name exists.

        Args:
            name: The Golden Config tree name to search for

        Returns:
            True if at least one tree with the specified name exists,
            False otherwise

        Raises:
            AsyncPlatformError: If the API request fails
        """
        configs = await self.configuration_manager.find_golden_configs(name=name)
        return len(configs) > 0

    async def _ensure_golden_config_is_new(self, name: str) -> None:
        """Ensure that a Golden Config tree with the given name does not exist.

        Args:
            name: The Golden Config tree name to check

        Raises:
            AsyncPlatformError: If a Golden Config tree with the name already exists
        """
        if await self.check_if_golden_config_exists(name):
            raise exceptions.AsyncPlatformError(
                f"Golden Config tree `{name}` already exists"
            )

    @logging.trace
    async def get_golden_config_by_name(self, name: str) -> dict[str, Any] | None:
        """Retrieve a Golden Config tree by name.

        Searches for a Golden Config tree by exact name and returns the first match.

        Args:
            name: The Golden Config tree name to search for

        Returns:
            The Golden Config tree dictionary if an exact name match is found,
            None otherwise

        Raises:
            AsyncPlatformError: If the API request fails
        """
        configs = await self.configuration_manager.find_golden_configs(name=name)
        return next((c for c in configs if c.get("name") == name), None)

    @logging.trace
    async def delete(self, name: str) -> None:
        """Delete a Golden Config tree by name.

        Searches for a Golden Config tree by name and deletes it if found.

        Args:
            name: The name of the Golden Config tree to delete

        Raises:
            AsyncPlatformError: If the delete operation fails
        """
        config = await self.get_golden_config_by_name(name)
        if config is not None:
            await self.configuration_manager.delete_golden_config(config["id"])

    @logging.trace
    async def importer(
        self,
        trees: list[dict[str, Any]],
        *,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Import one or more Golden Config trees with validation.

        Creates a deep copy of the input trees to avoid mutation, then imports
        them into the Configuration Manager. Typically used to restore exported
        trees or migrate configurations between environments.

        Args:
            trees: List of Golden Config tree objects to import. Each object
                contains a ``data`` key with a list of tree version summary
                documents.
            options: Optional import options dictionary

        Returns:
            A dictionary containing the import result with keys:
                - status: "success"
                - message: Human-readable summary (e.g. "2 golden config trees
                  imported successfully")

        Raises:
            AsyncPlatformError: If a Golden Config tree with the same name already
                exists, or if the import request fails or data is invalid
        """
        trees = copy.deepcopy(trees)

        for tree in trees:
            name = tree["data"][0]["name"]
            await self._ensure_golden_config_is_new(name)

        result = await self.configuration_manager.import_golden_config(
            trees, options=options
        )

        logging.info(f"Successfully imported {len(trees)} golden config tree(s)")

        return result

    @logging.trace
    async def import_golden_config(
        self,
        trees: list[dict[str, Any]],
        *,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Import one or more Golden Config trees.

        Delegates to the Configuration Manager service to insert the provided
        golden config tree documents into the platform. Typically used to restore
        exported trees or migrate configurations between environments.

        Args:
            trees: List of Golden Config tree objects to import. Each object
                contains a ``data`` key with a list of tree version summary
                documents.
            options: Optional import options dictionary

        Returns:
            A dictionary containing the import result with keys:
                - status: "success"
                - message: Human-readable summary (e.g. "2 golden config trees
                  imported successfully")

        Raises:
            AsyncPlatformError: If the import request fails or data is invalid
        """
        result = await self.configuration_manager.import_golden_config(
            trees, options=options
        )

        logging.info(f"Successfully imported {len(trees)} golden config tree(s)")

        return result

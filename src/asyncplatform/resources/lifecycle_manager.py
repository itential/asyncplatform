# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Lifecycle Manager resource for managing Itential Platform Lifecycle Manager resources

This module provides the Resource class for high-level lifecycle manager operations
including importing resource models, deleting resource models by name, importing
resource instances, and checking resource existence in the Lifecycle Manager service.
"""

from __future__ import annotations

from typing import Any

from asyncplatform import exceptions
from asyncplatform import logging
from asyncplatform.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing Lifecycle Manager resource models and instances.

    This resource provides high-level operations for lifecycle manager resource
    model management including importing resource models with validation, deleting
    resource models by name, and importing resource instances into models identified
    by name. It integrates with the Lifecycle Manager service to handle resource
    lifecycle operations.

    Attributes:
        lifecycle_manager: Property that returns the Lifecycle Manager
            service instance
    """

    name: str = "lifecycle_manager"

    async def _check_if_resource_exists(self, name: str) -> bool:
        """Check if a resource model with the given name exists.

        Args:
            name: The resource model name to search for

        Returns:
            True if at least one resource model with the specified name exists,
            False otherwise

        Raises:
            AsyncPlatformError: If the API request fails
        """
        resources = await self.lifecycle_manager.get_resources(**{"equals[name]": name})
        return any(resource["name"] == name for resource in resources)

    async def _ensure_resource_is_new(self, name: str) -> None:
        """Ensure that a resource model with the given name does not exist.

        Args:
            name: The resource model name to check

        Raises:
            AsyncPlatformError: If a resource model with the name already exists
        """
        if await self._check_if_resource_exists(name):
            raise exceptions.AsyncPlatformError(
                f"Resource model `{name}` already exists"
            )

    @logging.trace
    async def get_resource_by_id(self, resource_id: str) -> dict[str, Any]:
        """Retrieve a resource model by ID.

        Args:
            resource_id: The unique identifier of the resource model

        Returns:
            A dictionary containing the complete resource model data

        Raises:
            AsyncPlatformError: If the API request fails or the resource doesn't exist
        """
        return await self.lifecycle_manager.get_resource(resource_id)

    @logging.trace
    async def get_resource_by_name(self, name: str) -> dict[str, Any] | None:
        """Retrieve a resource model by name.

        Searches for a resource model by name and returns the first exact match.

        Args:
            name: The resource model name to search for

        Returns:
            The resource model dictionary if an exact name match is found,
            None otherwise

        Raises:
            AsyncPlatformError: If the API request fails
        """
        resources = await self.lifecycle_manager.get_resources(**{"equals[name]": name})
        return next(
            (resource for resource in resources if resource["name"] == name),
            None,
        )

    @logging.trace
    async def importer(
        self,
        resource_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Import a resource model into the Lifecycle Manager.

        Imports a resource model definition into the platform after optionally
        checking for duplicate names. When overwrite is False, raises an error
        if a resource model with the same name already exists.

        Args:
            resource_data: Complete resource model definition including name,
                description, schema, and actions

        Returns:
            A dictionary containing the imported resource model with assigned ID

        Raises:
            AsyncPlatformError: If overwrite is False and a resource model with
                the same name already exists, or if the import request fails
        """

        result = await self.lifecycle_manager.import_resource(resource_data)

        resource_name = result.get("name", resource_data.get("name"))
        resource_id = result.get("_id")

        logging.info(
            f"Successfully imported resource model {resource_name} (id: {resource_id})"
        )

        return result

    @logging.trace
    async def delete(self, name: str) -> dict[str, Any] | None:
        """Delete a resource model by name.

        Searches for a resource model by name and deletes it if found.

        Args:
            name: The name of the resource model to delete

        Returns:
            The deletion result dictionary if the resource was found and deleted,
            None if no resource with the specified name exists

        Raises:
            AsyncPlatformError: If the delete operation fails
        """
        resource = await self.get_resource_by_name(name)
        if resource is None:
            return None

        result = await self.lifecycle_manager.delete_resource(resource["_id"])

        logging.info(f"Successfully deleted resource model `{name}`")

        return result

    @logging.trace
    async def validate_actions(
        self,
        model_name: str,
        actions: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate action definitions for a resource model identified by name.

        Looks up the resource model by name and validates the provided action
        definitions against it without modifying the model. Raises an error if
        the resource model cannot be found.

        Args:
            model_name: The name of the resource model to validate actions for
            actions: A mapping containing the action definitions to validate

        Returns:
            A dictionary containing validation results and any errors

        Raises:
            AsyncPlatformError: If the resource model is not found or the
                validation request fails
        """
        resource = await self.get_resource_by_name(model_name)
        if resource is None:
            raise exceptions.AsyncPlatformError(
                f"Resource model `{model_name}` not found"
            )

        return await self.lifecycle_manager.validate_actions(resource["_id"], actions)

    @logging.trace
    async def import_instance(
        self,
        model_name: str,
        instance_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Import a resource instance into a resource model identified by name.

        Looks up the resource model by name and imports the provided instance
        data into it. Raises an error if the resource model cannot be found.

        Args:
            model_name: The name of the resource model to import the instance into
            instance_data: A mapping containing the complete instance data to import

        Returns:
            A dictionary containing the imported resource instance with assigned ID

        Raises:
            AsyncPlatformError: If the resource model is not found or the import
                request fails
        """
        resource = await self.get_resource_by_name(model_name)
        if resource is None:
            raise exceptions.AsyncPlatformError(
                f"Resource model `{model_name}` not found"
            )

        result = await self.lifecycle_manager.import_instance(
            resource["_id"], instance_data
        )

        instance_name = result.get("name", instance_data.get("name"))
        instance_id = result.get("_id")

        logging.info(
            f"Successfully imported instance {instance_name} (id: {instance_id}) "
            f"into resource model `{model_name}`"
        )

        return result

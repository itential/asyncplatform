# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import asyncio

from typing import Any

from asyncplatform import logging
from asyncplatform.http import HTTPStatus
from asyncplatform.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing Lifecycle Manager resources in Itential Platform.

    The Lifecycle Manager service provides methods for managing resource models,
    resource instances, and action executions. It enables CRUD operations on
    resources, importing/exporting resources and instances, running actions,
    and tracking action execution history.

    This service handles:
    - Resource model lifecycle (create, read, update, delete, import, export)
    - Resource instance management (create, read, update, import, export)
    - Action validation and execution
    - Action execution history tracking

    Inherits from ServiceBase and provides HTTP helper methods for interacting
    with the Lifecycle Manager API endpoints.

    Attributes:
        name: Service identifier for logging and identification
        PAGINATION_LIMIT: Number of items to fetch per page when retrieving all items
    """

    name: str = "lifecycle_manager"
    PAGINATION_LIMIT: int = 100

    async def _fetch_all_paginated(
        self,
        path: str,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """Fetch all items from a paginated endpoint.

        Private helper method that handles automatic pagination for any endpoint
        that returns paginated results. Makes concurrent requests for additional
        pages when the total exceeds the pagination limit.

        Args:
            path: API endpoint path to fetch from
            **filters: Optional query parameters for filtering results

        Returns:
            A list of all items from the paginated response. Returns an empty
            list if no items exist.

        Raises:
            AsyncPlatformError: If any API request fails during retrieval
        """
        limit = self.PAGINATION_LIMIT

        params = {"limit": limit, **filters}

        res = await self.get(path, params=params)
        json_data = res.json()

        total = json_data.get("metadata", {}).get("total", 0)

        if total == 0:
            return []

        data_key = "data" if "data" in json_data else "items"
        results = json_data[data_key]

        if total <= limit:
            return results

        tasks = [
            self.get(path, params={"limit": min(limit, total - skip), "skip": skip, **filters})
            for skip in range(limit, total, limit)
        ]

        task_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in task_results:
            if isinstance(result, Exception):
                raise result
            results.extend(result.json()[data_key])  # type: ignore[union-attr]

        return results

    # Action Execution Methods

    @logging.trace
    async def get_action_executions(self, **filters: Any) -> list[dict[str, Any]]:
        """Retrieve all resource action history documents.

        This method retrieves all action execution records with automatic pagination
        handling. If the total number of records exceeds the initial limit,
        additional concurrent requests are made to fetch all remaining records
        efficiently. Action executions track the history of actions run on resources.

        Args:
            **filters: Optional query parameters for filtering results. Supports
                Itential Platform query parameter patterns:

                - equals[field]: Exact match filtering
                - contains[field]: Partial string match filtering
                - exists[field]: Field existence check (true/false)
                - in[field]: Value in list filtering
                - sort: Sort order (prefix with "-" for descending)

                Example:
                    filters = {
                        "equals[status]": "completed",
                        "contains[actionName]": "provision",
                        "sort": "-createdAt"
                    }
                    await get_action_executions(**filters)

        Returns:
            A list of action execution dictionaries. Returns an empty list if
            no executions exist.

        Raises:
            AsyncPlatformError: If any API request fails during retrieval
        """
        return await self._fetch_all_paginated("/lifecycle-manager/action-executions", **filters)

    @logging.trace
    async def get_action_execution(self, execution_id: str) -> dict[str, Any]:
        """Get a single action execution record by ID.

        Retrieves detailed information about a specific action execution,
        including status, results, and execution metadata.

        Args:
            execution_id: The unique identifier of the action execution

        Returns:
            A dictionary containing the complete action execution record

        Raises:
            AsyncPlatformError: If the API request fails or execution doesn't exist
        """
        res = await self.get(f"/lifecycle-manager/action-executions/{execution_id}")
        return res.json()

    # Resource Model Methods

    @logging.trace
    async def get_resources(self, **filters: Any) -> list[dict[str, Any]]:
        """Retrieve all resource models.

        This method retrieves all resource models with automatic pagination handling.
        If the total number of resources exceeds the initial limit, additional
        concurrent requests are made to fetch all remaining resources efficiently.
        Resource models define the structure and behavior of lifecycle resources.

        Args:
            **filters: Optional query parameters for filtering results. Supports
                Itential Platform query parameter patterns:

                - equals[field]: Exact match filtering
                - contains[field]: Partial string match filtering
                - exists[field]: Field existence check (true/false)
                - in[field]: Value in list filtering
                - sort: Sort order (prefix with "-" for descending)

                Example:
                    filters = {
                        "equals[name]": "NetworkDevice",
                        "contains[description]": "router",
                        "sort": "name"
                    }
                    await get_resources(**filters)

        Returns:
            A list of resource model dictionaries. Returns an empty list if
            no resources exist.

        Raises:
            AsyncPlatformError: If any API request fails during retrieval
        """
        return await self._fetch_all_paginated("/lifecycle-manager/resources", **filters)

    @logging.trace
    async def create_resource(self, resource_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new resource model.

        Creates a new resource model with the specified configuration. The resource
        model defines the structure, fields, and actions available for resource
        instances.

        Args:
            resource_data: A mapping containing the resource model definition
                including name, description, schema, and actions

        Returns:
            A dictionary containing the created resource model with assigned ID

        Raises:
            AsyncPlatformError: If the creation request fails or data is invalid
        """
        res = await self.post(
            "/lifecycle-manager/resources",
            json=resource_data,
            expected_status=HTTPStatus.CREATED,
        )
        return res.json()

    @logging.trace
    async def get_resource(self, resource_id: str) -> dict[str, Any]:
        """Get a resource model by ID.

        Retrieves detailed information about a specific resource model including
        its schema, actions, and configuration.

        Args:
            resource_id: The unique identifier of the resource model

        Returns:
            A dictionary containing the complete resource model data

        Raises:
            AsyncPlatformError: If the API request fails or resource doesn't exist
        """
        res = await self.get(f"/lifecycle-manager/resources/{resource_id}")
        return res.json()

    @logging.trace
    async def update_resource(
        self,
        resource_id: str,
        resource_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a resource model.

        Performs a complete update (PUT) on a resource model, replacing the
        entire resource definition with the provided data.

        Args:
            resource_id: The unique identifier of the resource model to update
            resource_data: A mapping containing the complete updated resource
                model definition

        Returns:
            A dictionary containing the updated resource model

        Raises:
            AsyncPlatformError: If the update request fails or resource doesn't exist
        """
        res = await self.put(
            f"/lifecycle-manager/resources/{resource_id}",
            json=resource_data,
        )
        return res.json()

    @logging.trace
    async def delete_resource(self, resource_id: str) -> dict[str, Any]:
        """Delete a resource model.

        Permanently removes a resource model and optionally its instances from
        the platform. This operation cannot be undone.

        Args:
            resource_id: The unique identifier of the resource model to delete

        Returns:
            A dictionary containing the deletion result

        Raises:
            AsyncPlatformError: If the deletion request fails or resource doesn't exist
        """
        res = await self.delete(
            f"/lifecycle-manager/resources/{resource_id}",
            expected_status=HTTPStatus.OK,
        )
        return res.json()

    @logging.trace
    async def edit_resource(
        self,
        model_id: str,
        edits: dict[str, Any],
    ) -> dict[str, Any]:
        """Perform edits to a resource model.

        Applies a set of edit operations to a resource model. This endpoint
        supports specific edit operations beyond simple field updates.

        Args:
            model_id: The unique identifier of the resource model to edit
            edits: A mapping containing the edit operations to perform

        Returns:
            A dictionary containing the edited resource model

        Raises:
            AsyncPlatformError: If the edit request fails or model doesn't exist
        """
        res = await self.post(
            f"/lifecycle-manager/resources/{model_id}/edit",
            json=edits,
        )
        return res.json()

    @logging.trace
    async def import_resource(self, resource_data: dict[str, Any]) -> dict[str, Any]:
        """Import a resource model.

        Imports a resource model definition into the platform. This is typically
        used to restore exported resources or migrate resources between environments.

        Args:
            resource_data: A mapping containing the complete resource model
                definition to import

        Returns:
            A dictionary containing the imported resource model with assigned ID

        Raises:
            AsyncPlatformError: If the import request fails or data is invalid
        """
        res = await self.post(
            "/lifecycle-manager/resources/import",
            json=resource_data,
        )
        return res.json()

    @logging.trace
    async def export_resource(self, model_id: str) -> dict[str, Any]:
        """Export a resource model.

        Exports a resource model definition in a format suitable for backup
        or migration to another environment.

        Args:
            model_id: The unique identifier of the resource model to export

        Returns:
            A dictionary containing the complete exportable resource model definition

        Raises:
            AsyncPlatformError: If the export request fails or model doesn't exist
        """
        res = await self.get(f"/lifecycle-manager/resources/{model_id}/export")
        return res.json()

    @logging.trace
    async def validate_actions(
        self,
        model_id: str,
        actions: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate the actions defined on a resource model.

        Validates action definitions without modifying the resource model.
        This helps ensure actions are correctly configured before saving.

        Args:
            model_id: The unique identifier of the resource model
            actions: A mapping containing the action definitions to validate

        Returns:
            A dictionary containing validation results and any errors

        Raises:
            AsyncPlatformError: If the validation request fails
        """
        res = await self.post(
            f"/lifecycle-manager/resources/{model_id}/actions/validate",
            json=actions,
        )
        return res.json()

    @logging.trace
    async def run_action(
        self,
        model_id: str,
        action_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Run a resource action.

        Executes an action defined on a resource model. Actions can perform
        various operations on resource instances such as provisioning,
        deprovisioning, or custom operations.

        Args:
            model_id: The unique identifier of the resource model
            action_data: A mapping containing the action execution parameters
                including action name and input data

        Returns:
            A dictionary containing the action execution result and status

        Raises:
            AsyncPlatformError: If the action execution fails
        """
        res = await self.post(
            f"/lifecycle-manager/resources/{model_id}/run-action",
            json=action_data,
        )
        return res.json()

    # Resource Instance Methods

    @logging.trace
    async def get_instances(
        self,
        model_id: str,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """Retrieve all resource instances for a specific model.

        This method retrieves all resource instances belonging to a specific
        resource model with automatic pagination handling. If the total number
        of instances exceeds the initial limit, additional concurrent requests
        are made to fetch all remaining instances efficiently.

        Args:
            model_id: The unique identifier of the resource model
            **filters: Optional query parameters for filtering results. Supports
                Itential Platform query parameter patterns:

                - equals[field]: Exact match filtering
                - contains[field]: Partial string match filtering
                - exists[field]: Field existence check (true/false)
                - in[field]: Value in list filtering
                - sort: Sort order (prefix with "-" for descending)

                Example:
                    filters = {
                        "equals[name]": "prod-router-01",
                        "contains[ipAddress]": "10.0.",
                        "sort": "-createdAt"
                    }
                    await get_instances("model_id", **filters)

        Returns:
            A list of resource instance dictionaries. Returns an empty list if
            no instances exist.

        Raises:
            AsyncPlatformError: If any API request fails or model doesn't exist
        """
        return await self._fetch_all_paginated(
            f"/lifecycle-manager/resources/{model_id}/instances",
            **filters,
        )

    @logging.trace
    async def get_instance(self, model_id: str, instance_id: str) -> dict[str, Any]:
        """Get a single resource instance.

        Retrieves detailed information about a specific resource instance
        including its current state and field values.

        Args:
            model_id: The unique identifier of the resource model
            instance_id: The unique identifier of the resource instance

        Returns:
            A dictionary containing the complete resource instance data

        Raises:
            AsyncPlatformError: If the API request fails or instance doesn't exist
        """
        res = await self.get(
            f"/lifecycle-manager/resources/{model_id}/instances/{instance_id}"
        )
        return res.json()

    @logging.trace
    async def update_instance(
        self,
        model_id: str,
        instance_id: str,
        instance_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a resource instance.

        Updates the name and description fields of a resource instance.
        Other field updates may require running specific actions.

        Args:
            model_id: The unique identifier of the resource model
            instance_id: The unique identifier of the resource instance
            instance_data: A mapping containing the updated name and/or
                description fields

        Returns:
            A dictionary containing the updated resource instance

        Raises:
            AsyncPlatformError: If the update request fails or instance doesn't exist
        """
        res = await self.put(
            f"/lifecycle-manager/resources/{model_id}/instances/{instance_id}",
            json=instance_data,
        )
        return res.json()

    @logging.trace
    async def import_instance(
        self,
        model_identifier: str,
        instance_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Import an instance into a resource.

        Imports a resource instance into the specified resource model. This is
        typically used to restore exported instances or migrate instances between
        environments.

        Args:
            model_identifier: The identifier of the resource model (ID or name)
            instance_data: A mapping containing the complete instance data to import

        Returns:
            A dictionary containing the imported resource instance with assigned ID

        Raises:
            AsyncPlatformError: If the import request fails or data is invalid
        """
        res = await self.post(
            f"/lifecycle-manager/resources/{model_identifier}/instances/import",
            json=instance_data,
        )
        return res.json()

    @logging.trace
    async def export_instance(
        self,
        model_identifier: str,
        instance_identifier: str,
    ) -> dict[str, Any]:
        """Export a resource instance.

        Exports a resource instance in a format suitable for backup or migration
        to another environment.

        Args:
            model_identifier: The identifier of the resource model (ID or name)
            instance_identifier: The identifier of the resource instance (ID or name)

        Returns:
            A dictionary containing the complete exportable instance definition

        Raises:
            AsyncPlatformError: If the export request fails or instance doesn't exist
        """
        res = await self.get(
            f"/lifecycle-manager/resources/{model_identifier}/instances/{instance_identifier}/export"
        )
        return res.json()

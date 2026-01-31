# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import asyncio

from typing import Any

from asyncplatform import logging
from asyncplatform.http import HTTPStatus
from asyncplatform.services import ServiceBase

# Page size for paginated API requests
_PAGE_LIMIT = 100


class Service(ServiceBase):
    """Service class for managing Configuration Manager in Itential Platform.

    The Service provides methods for interacting with the Configuration Manager,
    including device management, backups, compliance plans, templates, and device
    groups. Configuration Manager is the core service for managing network device
    configurations, compliance, and templates.

    All paginated methods automatically fetch all results using concurrent requests
    for optimal performance.

    Attributes:
        name: Service identifier for logging and identification
    """

    name: str = "configuration_manager"

    async def _get_paginated_devices(
        self,
        *,
        filter: dict[str, Any] | None = None,
        adapter_type: list[str] | None = None,
        adapter_id: list[str] | None = None,
        exact_match: bool = False,
    ) -> list[dict[str, Any]]:
        """Fetch all devices with automatic pagination handling.

        Makes an initial request to determine total count, then creates concurrent
        tasks for remaining pages if needed.

        Args:
            filter: Optional filter criteria dictionary. Supported keys:
                - name (str): Device name to match
                - address (str): Device IP address (e.g., "10.1.98.234")
                - port (str): Device port number as string (e.g., "22")
                Example: {"name": "router1", "address": "10.0.0.1"}
            adapter_type: Optional list of adapter types to filter by
            adapter_id: Optional list of adapter IDs to filter by
            exact_match: Whether to use exact matching for filters

        Returns:
            A list of all device objects matching the criteria

        Raises:
            AsyncPlatformError: If any API request fails
        """
        # Build options dict, filtering out None values
        options = {
            "start": 0,
            "limit": _PAGE_LIMIT,
            **{
                k: v
                for k, v in {
                    "filter": filter,
                    "adapterType": adapter_type,
                    "adapterId": adapter_id,
                    "exactMatch": exact_match if exact_match else None,
                }.items()
                if v is not None
            },
        }

        # Make initial request to get total count and first page
        res = await self.post(
            "/configuration_manager/devices",
            json={"options": options},
            expected_status=HTTPStatus.OK,
        )

        json_data = res.json()
        total = json_data["total"]

        # Handle empty results
        if total == 0:
            return []

        # If all results fit in first page, return immediately
        if total <= _PAGE_LIMIT:
            return json_data["list"]

        # Start with first page results
        results = json_data["list"]

        # Create tasks for remaining pages
        tasks = []
        for start in range(_PAGE_LIMIT, total, _PAGE_LIMIT):
            page_options = options.copy()
            page_options["start"] = start

            tasks.append(
                self.post(
                    "/configuration_manager/devices",
                    json={"options": page_options},
                    expected_status=HTTPStatus.OK,
                )
            )

        # Fetch all remaining pages concurrently
        if tasks:
            task_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check for exceptions in results
            for result in task_results:
                if isinstance(result, Exception):
                    raise result

            # Combine all page results
            for result in task_results:
                results.extend(result.json()["list"])  # type: ignore[union-attr]

        return results

    async def _get_paginated_backups(
        self,
        *,
        filter: dict[str, Any] | None = None,
        regex: bool = False,
    ) -> list[dict[str, Any]]:
        """Fetch all backups with automatic pagination handling.

        Makes an initial request to determine total count, then creates concurrent
        tasks for remaining pages if needed.

        Args:
            filter: Optional filter criteria dictionary. Supported keys:
                - name (str): Device name to match backups for
                Example: {"name": "router1"}
            regex: Whether to use regex matching in filters (default: False)

        Returns:
            A list of all backup objects matching the criteria

        Raises:
            AsyncPlatformError: If any API request fails
        """
        # Build options dict, filtering out None values
        options = {
            "start": 0,
            "limit": _PAGE_LIMIT,
            **{
                k: v
                for k, v in {
                    "filter": filter,
                    "regex": regex if regex else None,
                }.items()
                if v is not None
            },
        }

        # Make initial request to get total count and first page
        res = await self.post(
            "/configuration_manager/backups",
            json={"options": options},
            expected_status=HTTPStatus.OK,
        )

        json_data = res.json()
        total = json_data["total"]

        # Handle empty results
        if total == 0:
            return []

        # If all results fit in first page, return immediately
        if total <= _PAGE_LIMIT:
            return json_data["list"]

        # Start with first page results
        results = json_data["list"]

        # Create tasks for remaining pages
        tasks = []
        for start in range(_PAGE_LIMIT, total, _PAGE_LIMIT):
            page_options = options.copy()
            page_options["start"] = start

            tasks.append(
                self.post(
                    "/configuration_manager/backups",
                    json={"options": page_options},
                    expected_status=HTTPStatus.OK,
                )
            )

        # Fetch all remaining pages concurrently
        if tasks:
            task_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check for exceptions in results
            for result in task_results:
                if isinstance(result, Exception):
                    raise result

            # Combine all page results
            for result in task_results:
                results.extend(result.json()["list"])  # type: ignore[union-attr]

        return results

    # Device Management

    @logging.trace
    async def get_devices(
        self,
        *,
        filter: dict[str, Any] | None = None,
        adapter_type: list[str] | None = None,
        adapter_id: list[str] | None = None,
        exact_match: bool = False,
    ) -> list[dict[str, Any]]:
        """Retrieve all devices with automatic pagination.

        Fetches all devices from Configuration Manager with support for filtering
        by name, address, port, adapter type, and adapter ID. Automatically
        handles pagination by fetching all pages concurrently.

        Args:
            filter: Optional filter criteria dictionary. Supported keys:
                - name (str): Device name to match
                - address (str): Device IP address (e.g., "10.1.98.234")
                - port (str): Device port number as string (e.g., "22")
                Example: {"name": "router1", "address": "10.0.0.1"}
            adapter_type: Optional list of adapter types to filter by.
                Example: ["NSO", "AnsibleManager"]
            adapter_id: Optional list of adapter IDs to filter by.
                Example: ["ansible-us-east"]
            exact_match: Whether to use exact matching for filters (default: False)

        Returns:
            A list of all device objects matching the criteria

        Raises:
            AsyncPlatformError: If the API request fails
        """
        return await self._get_paginated_devices(
            filter=filter,
            adapter_type=adapter_type,
            adapter_id=adapter_id,
            exact_match=exact_match,
        )

    @logging.trace
    async def get_device(self, device_name: str) -> dict[str, Any]:
        """Retrieve detailed information about a specific device by name.

        Args:
            device_name: The name of the device to retrieve

        Returns:
            A dictionary containing the complete device data

        Raises:
            AsyncPlatformError: If the API request fails or device doesn't exist
        """
        res = await self.get(f"/configuration_manager/devices/{device_name}")
        return res.json()

    @logging.trace
    async def get_device_configuration(
        self,
        device_name: str,
        format: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve device configuration in specified format.

        Args:
            device_name: The name of the device
            format: Optional format for the configuration

        Returns:
            A dictionary containing the device configuration

        Raises:
            AsyncPlatformError: If the API request fails
        """
        path = (
            f"/configuration_manager/devices/{device_name}/configuration/{format}"
            if format
            else f"/configuration_manager/devices/{device_name}/configuration"
        )

        res = await self.get(path)
        return res.json()

    @logging.trace
    async def patch_device(
        self,
        device_name: str,
        data: dict[str, Any],
        *,
        advanced: bool = False,
    ) -> dict[str, Any]:
        """Update device configuration with partial changes.

        Args:
            device_name: The name of the device to update
            data: Dictionary containing the fields to update
            advanced: Whether to use advanced patching (default: False)

        Returns:
            The response from the patch operation

        Raises:
            AsyncPlatformError: If the update request fails
        """
        path = (
            f"/configuration_manager/patch_device/advanced/{device_name}"
            if advanced
            else f"/configuration_manager/patch_device/{device_name}"
        )

        res = await self.patch(path, json=data)
        return res.json()

    @logging.trace
    async def check_device_alive(self, device_name: str) -> dict[str, Any]:
        """Check if a device is alive and reachable.

        Args:
            device_name: The name of the device to check

        Returns:
            A dictionary containing the device alive status

        Raises:
            AsyncPlatformError: If the API request fails
        """
        res = await self.get(f"/configuration_manager/devices/{device_name}/isAlive")
        return res.json()

    # Backup Management

    @logging.trace
    async def get_backups(
        self,
        *,
        filter: dict[str, Any] | None = None,
        regex: bool = False,
    ) -> list[dict[str, Any]]:
        """Retrieve all device backups with automatic pagination.

        Fetches all backups with optional filtering. Automatically handles
        pagination by fetching all pages concurrently.

        Args:
            filter: Optional filter criteria dictionary. Supported keys:
                - name (str): Device name to match backups for
                Example: {"name": "router1"}
            regex: Whether to use regex matching in filters (default: False)

        Returns:
            A list of all backup objects matching the criteria

        Raises:
            AsyncPlatformError: If the API request fails
        """
        return await self._get_paginated_backups(
            filter=filter,
            regex=regex,
        )

    @logging.trace
    async def get_backup(self, backup_id: str) -> dict[str, Any]:
        """Retrieve a specific backup by ID.

        Args:
            backup_id: The unique identifier of the backup

        Returns:
            A dictionary containing the backup data

        Raises:
            AsyncPlatformError: If the API request fails or backup doesn't exist
        """
        res = await self.get(f"/configuration_manager/backups/{backup_id}")
        return res.json()

    @logging.trace
    async def delete_backups(self, backup_ids: list[str]) -> dict[str, Any]:
        """Delete one or more device backups by ID.

        Args:
            backup_ids: List of backup IDs to delete

        Returns:
            A dictionary containing deletion status with keys:
                - status: "success" or "conflict"
                - deleted: Number of backups deleted

        Raises:
            AsyncPlatformError: If the deletion request fails
        """
        res = await self.delete(
            "/configuration_manager/backups",
            params={"backupIds": backup_ids},
        )
        return res.json()

    # Device Group Management

    @logging.trace
    async def get_device_groups(self) -> list[dict[str, Any]]:
        """Retrieve all device groups.

        Returns:
            A list of device group objects

        Raises:
            AsyncPlatformError: If the API request fails
        """
        res = await self.get("/configuration_manager/deviceGroups")
        return res.json()

    @logging.trace
    async def get_device_group(self, group_id: str) -> dict[str, Any]:
        """Retrieve a specific device group by ID.

        Args:
            group_id: The unique identifier of the device group

        Returns:
            A dictionary containing the device group data

        Raises:
            AsyncPlatformError: If the API request fails or group doesn't exist
        """
        res = await self.get(f"/configuration_manager/deviceGroups/{group_id}")
        return res.json()

    @logging.trace
    async def delete_device_groups(self, group_ids: list[str]) -> dict[str, Any]:
        """Delete one or more device groups by ID.

        Args:
            group_ids: List of device group IDs to delete

        Returns:
            A dictionary containing deletion status

        Raises:
            AsyncPlatformError: If the deletion request fails
        """
        res = await self.delete(
            "/configuration_manager/deviceGroups",
            params={"groupIds": group_ids},
        )
        return res.json()

    @logging.trace
    async def search_device_groups(self, query: dict[str, Any]) -> dict[str, Any]:
        """Search for device groups using query criteria.

        Args:
            query: Query criteria for searching device groups

        Returns:
            A dictionary containing search results

        Raises:
            AsyncPlatformError: If the search request fails
        """
        res = await self.post(
            "/configuration_manager/deviceGroups/search",
            json=query,
            expected_status=HTTPStatus.OK,
        )
        return res.json()

    # Compliance Plan Management

    @logging.trace
    async def create_compliance_plan(
        self,
        name: str,
        *,
        description: str | None = None,
        nodes: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a new compliance plan.

        Args:
            name: Name of the compliance plan
            description: Optional description of the compliance plan
            nodes: Optional list of nodes to include in the plan, each containing:
                - treeId: The treeId of the golden config
                - version: The version of the golden config tree
                - nodeId: The configId of the node
                - variables: Optional variables dictionary
                - devices: Optional list of device names
                - deviceGroups: Optional list of device group IDs
                - tasks: Optional list of task IDs

        Returns:
            A dictionary containing the newly created compliance plan data

        Raises:
            AsyncPlatformError: If the creation request fails
        """
        # Build options dict, filtering out None values
        options = {
            k: v
            for k, v in {"description": description, "nodes": nodes}.items()
            if v is not None
        }

        payload: dict[str, Any] = {"name": name}
        if options:
            payload["options"] = options

        res = await self.post(
            "/configuration_manager/compliance_plans",
            json=payload,
            expected_status=HTTPStatus.OK,
        )

        logging.info(f"Created compliance plan: {name}")

        return res.json()

    @logging.trace
    async def update_compliance_plan(
        self,
        plan_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        nodes: list[dict[str, Any]] | None = None,
        gbac: dict[str, list[str]] | None = None,
    ) -> dict[str, Any]:
        """Update an existing compliance plan.

        Args:
            plan_id: The unique identifier of the compliance plan to update
            name: Optional new name for the compliance plan
            description: Optional new description
            nodes: Optional updated list of nodes
            gbac: Optional group-based access control settings with 'read' and 'write' arrays

        Returns:
            A dictionary containing update status with keys:
                - status: "success"
                - message: Status message

        Raises:
            AsyncPlatformError: If the update request fails
        """
        # Build options dict, filtering out None values
        options = {
            k: v
            for k, v in {
                "name": name,
                "description": description,
                "nodes": nodes,
                "gbac": gbac,
            }.items()
            if v is not None
        }

        res = await self.put(
            "/configuration_manager/compliance_plans",
            json={"planId": plan_id, "options": options},
        )

        logging.info(f"Updated compliance plan: {plan_id}")

        return res.json()

    @logging.trace
    async def delete_compliance_plans(self, plan_ids: list[str]) -> dict[str, Any]:
        """Delete one or more compliance plans by ID.

        Args:
            plan_ids: List of compliance plan IDs to delete

        Returns:
            A dictionary containing deletion status with keys:
                - status: Status string
                - deleted: Number of plans deleted

        Raises:
            AsyncPlatformError: If the deletion request fails
        """
        res = await self.delete(
            "/configuration_manager/compliance_plans",
            params={"planIds": plan_ids},
        )
        return res.json()

    @logging.trace
    async def get_compliance_plan(self, plan_id: str) -> dict[str, Any]:
        """Retrieve a specific compliance plan by ID.

        Args:
            plan_id: The unique identifier of the compliance plan

        Returns:
            A dictionary containing the compliance plan data

        Raises:
            AsyncPlatformError: If the API request fails or plan doesn't exist
        """
        res = await self.get(f"/configuration_manager/compliance_plans/{plan_id}")
        return res.json()

    @logging.trace
    async def search_compliance_plans(self, query: dict[str, Any]) -> dict[str, Any]:
        """Search for compliance plans using query criteria.

        Args:
            query: Query criteria for searching compliance plans

        Returns:
            A dictionary containing search results

        Raises:
            AsyncPlatformError: If the search request fails
        """
        res = await self.post(
            "/configuration_manager/search/compliance_plans",
            json=query,
            expected_status=HTTPStatus.OK,
        )
        return res.json()

    @logging.trace
    async def run_compliance_plan(self, plan_data: dict[str, Any]) -> dict[str, Any]:
        """Execute a compliance plan.

        Args:
            plan_data: Data required to run the compliance plan

        Returns:
            A dictionary containing the execution results

        Raises:
            AsyncPlatformError: If the execution request fails
        """
        res = await self.post(
            "/configuration_manager/compliance_plans/run",
            json=plan_data,
            expected_status=HTTPStatus.OK,
        )
        return res.json()

    # Template Management

    @logging.trace
    async def create_template(
        self,
        name: str,
        template: str,
        *,
        variables: dict[str, Any] | None = None,
        device_os_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new device template.

        Args:
            name: Name of the template
            template: Template content (Jinja2 format)
            variables: Optional default variables for the template
            device_os_types: Optional list of device OS types this template applies to

        Returns:
            A dictionary containing the newly created template with keys:
                - id: Template unique identifier
                - name: Template name
                - template: Template content
                - variables: Template variables
                - created: Creation timestamp
                - updated: Last update timestamp
                - createdBy: Creator user ID
                - updatedBy: Last updater user ID
                - gbac: Group-based access control settings

        Raises:
            AsyncPlatformError: If the creation request fails
        """
        payload: dict[str, Any] = {"name": name, "template": template}

        if variables is not None:
            payload["variables"] = variables

        if device_os_types is not None:
            payload["options"] = {"deviceOSTypes": device_os_types}

        res = await self.post(
            "/configuration_manager/templates",
            json=payload,
            expected_status=HTTPStatus.OK,
        )

        json_data = res.json()
        template_id = json_data["data"]["id"]

        logging.info(f"Created template: {name} (id: {template_id})")

        return json_data["data"]

    @logging.trace
    async def update_template(
        self,
        template_id: str,
        *,
        name: str | None = None,
        template: str | None = None,
        variables: dict[str, Any] | None = None,
        device_os_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update an existing device template.

        Args:
            template_id: The unique identifier of the template to update
            name: Optional new name for the template
            template: Optional new template content
            variables: Optional new variables
            device_os_types: Optional new list of device OS types

        Returns:
            A dictionary containing update status with keys:
                - status: "success"
                - updated: Number of templates updated

        Raises:
            AsyncPlatformError: If the update request fails
        """
        # Build data dict, filtering out None values
        data = {
            k: v
            for k, v in {
                "name": name,
                "template": template,
                "variables": variables,
            }.items()
            if v is not None
        }

        payload: dict[str, Any] = {"id": template_id, "data": data}

        if device_os_types is not None:
            payload["options"] = {"deviceOSTypes": device_os_types}

        res = await self.put("/configuration_manager/templates", json=payload)

        logging.info(f"Updated template: {template_id}")

        return res.json()

    @logging.trace
    async def delete_templates(self, template_ids: list[str]) -> dict[str, Any]:
        """Delete one or more device templates by ID.

        Args:
            template_ids: List of template IDs to delete

        Returns:
            A dictionary containing deletion status with keys:
                - status: "success" or "conflict"
                - deleted: Number of templates deleted

        Raises:
            AsyncPlatformError: If the deletion request fails
        """
        res = await self.delete(
            "/configuration_manager/templates",
            params={"templateIds": template_ids},
        )
        return res.json()

    @logging.trace
    async def get_templates(
        self,
        *,
        name: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for device templates.

        Args:
            name: Optional template name to search for
            options: Optional additional search options

        Returns:
            A list of template objects matching the search criteria. Each template
            contains keys like id, name, template, variables, created, updated, etc.

        Raises:
            AsyncPlatformError: If the search request fails
        """
        # Build payload dict, filtering out None values
        payload = {
            k: v for k, v in {"name": name, "options": options}.items() if v is not None
        }

        res = await self.post(
            "/configuration_manager/templates/search",
            json=payload,
            expected_status=HTTPStatus.OK,
        )

        json_data = res.json()
        return json_data["list"]

    @logging.trace
    async def apply_template(self, template_data: dict[str, Any]) -> dict[str, Any]:
        """Apply a template to devices.

        Args:
            template_data: Data required to apply the template, including
                template ID, target devices, and variable values

        Returns:
            A dictionary containing the application results

        Raises:
            AsyncPlatformError: If the application request fails
        """
        res = await self.post(
            "/configuration_manager/templates/apply",
            json=template_data,
            expected_status=HTTPStatus.OK,
        )
        return res.json()

    # Compliance Report Management

    @logging.trace
    async def get_compliance_reports(
        self,
        *,
        query: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Retrieve compliance reports.

        Args:
            query: Optional query criteria for filtering reports

        Returns:
            A dictionary containing compliance reports

        Raises:
            AsyncPlatformError: If the API request fails
        """
        if query is not None:
            res = await self.post(
                "/configuration_manager/compliance_reports",
                json=query,
                expected_status=HTTPStatus.OK,
            )
        else:
            res = await self.get("/configuration_manager/compliance_reports")

        return res.json()

    @logging.trace
    async def get_compliance_report_details(self, report_id: str) -> dict[str, Any]:
        """Retrieve detailed information about a specific compliance report.

        Args:
            report_id: The unique identifier of the compliance report

        Returns:
            A dictionary containing detailed compliance report data

        Raises:
            AsyncPlatformError: If the API request fails or report doesn't exist
        """
        res = await self.get(
            f"/configuration_manager/compliance_reports/details/{report_id}"
        )
        return res.json()

    @logging.trace
    async def get_compliance_report_history(
        self,
        *,
        query: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Retrieve compliance report history.

        Args:
            query: Optional query criteria for filtering history

        Returns:
            A dictionary containing compliance report history

        Raises:
            AsyncPlatformError: If the API request fails
        """
        if query is not None:
            res = await self.post(
                "/configuration_manager/compliance_reports/history",
                json=query,
                expected_status=HTTPStatus.OK,
            )
        else:
            res = await self.get("/configuration_manager/compliance_reports/history")

        return res.json()

    # Configuration Management

    @logging.trace
    async def get_configs(
        self,
        tree_id: str,
        *,
        version: str | None = None,
        node_path: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve configuration tree or specific node.

        Args:
            tree_id: The unique identifier of the configuration tree
            version: Optional version of the configuration tree
            node_path: Optional path to a specific node in the tree

        Returns:
            A dictionary containing the configuration data

        Raises:
            AsyncPlatformError: If the API request fails
        """
        if version is not None and node_path is not None:
            path = f"/configuration_manager/configs/{tree_id}/{version}/{node_path}"
        elif version is not None:
            path = f"/configuration_manager/configs/{tree_id}/{version}"
        else:
            path = f"/configuration_manager/configs/{tree_id}"

        res = await self.get(path)
        return res.json()

    @logging.trace
    async def search_configs(self, query: dict[str, Any]) -> dict[str, Any]:
        """Search for configurations using query criteria.

        Args:
            query: Query criteria for searching configurations

        Returns:
            A dictionary containing search results

        Raises:
            AsyncPlatformError: If the search request fails
        """
        res = await self.post(
            "/configuration_manager/search/configs",
            json=query,
            expected_status=HTTPStatus.OK,
        )
        return res.json()

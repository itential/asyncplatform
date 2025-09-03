# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from collections.abc import Mapping

from asyncplatform import logging
from asyncplatform.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing Operations Manager automations in Itential Platform.

    The Service provides methods for interacting with Operations Manager
    automations, including searching, importing, and deleting automation
    configurations. Automations define reusable automation components that
    can be executed across the platform.

    Args:
        ctx: Context object containing the platform client and shared resources

    Attributes:
        name: Service identifier for logging and identification
    """

    name: str = "operations_manager"

    @logging.trace
    async def find_automations(self, *,
                               name: str | None = None) -> list[dict[str, Any]]:
        """Search for Operations Manager automations with automatic pagination.

        Queries the platform for automations matching the specified criteria. If no
        name is provided, returns all automations. Automatically handles pagination
        to retrieve all matching results across multiple pages.

        Args:
            name: Optional automation name to search for using exact match. If None,
                no name filtering is applied

        Returns:
            A list of automation dictionaries matching the search criteria. Each
            automation includes id, name, description, component details, and GBAC
            configuration. Returns an empty list if no matching automations are found.

        Raises:
            HTTPError: If any API request fails during automation retrieval
        """
        limit = 100
        params: dict[str, Any] = {"limit": limit}

        if name is not None:
            params.update({
                "equalsField": "name",
                "equals": name
            })

        res = await self.get(
            "/operations-manager/automations",
            params=params
        )

        json_data = res.json()

        total = json_data["metadata"]["total"]

        logging.info(f"Found {total} automation(s)")

        if total == 0:
            return []

        if total <= limit:
            return json_data["data"]

        tasks = []
        results = json_data["data"]

        for skip in range(limit, total, limit):
            remaining = total - skip
            fetch_limit = min(limit, remaining)

            page_params = params.copy()
            page_params.update({"limit": fetch_limit, "skip": skip})

            tasks.append(self.get(
                "/operations-manager/automations",
                params=page_params
            ))

        if tasks:
            task_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in task_results:
                if isinstance(result, Exception):
                    raise result
                results.extend(result["data"])  # type: ignore[index]

        return results


    @logging.trace
    async def import_automation(self, automation: Mapping[str, Any]) -> dict[str, Any]:
        """Import an automation into Operations Manager.

        Imports an automation configuration into the Itential Platform. The automation
        can reference workflows or other components.

        Args:
            automation: A mapping containing the complete automation definition including
                name, description, componentName, componentType, and componentId

        Returns:
            A dictionary containing the imported automation data, including the newly
            assigned automation ID (_id) and complete automation configuration

        Raises:
            HTTPError: If the import request fails or the automation format is invalid
        """
        res = await self.put(
            "/operations-manager/automations",
            json={"automations": [automation]}
        )

        json_data = res.json()

        logging.info(json_data["message"])

        return json_data["data"][0]["data"]


    @logging.trace
    async def delete_automation(self, object_id: str) -> dict[str, Any]:
        """Delete an Operations Manager automation by ID.

        Permanently removes an automation from the platform. This operation
        cannot be undone.

        Args:
            object_id: The unique identifier (_id) of the automation to delete

        Returns:
            A dictionary containing the deletion result

        Raises:
            HTTPError: If the deletion request fails or automation doesn't exist
        """
        res = await self.delete(
            f"/operations-manager/automations/{object_id}"
        )

        logging.info(f"Successfully deleted automation with id {object_id}")

        return res.json()

    @logging.trace
    async def update_automation(
        self, automation: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an automation in Operations Manager.

        Args:
            automation: The automation data containing _id and updated fields

        Returns:
            The updated automation data

        Raises:
            HTTPError: If the API request fails
        """
        object_id = automation["_id"]
        res = await self.patch(
            f"/operations-manager/automations/{object_id}",
            json=automation
        )
        json_data = res.json()
        logging.info(json_data["message"])
        return json_data["data"]

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
from asyncplatform.exceptions import AsyncPlatformError
from asyncplatform.http import HTTPStatus
from asyncplatform.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing integration instances in Itential Platform.

    Provides methods for interacting with integration instance resources,
    including searching, retrieving, creating, and deleting instances.
    Integration instances are active connections to external systems created
    from integration models.

    Attributes:
        name: Service identifier for logging and identification
        PAGINATION_LIMIT: Number of items to fetch per page
    """

    name: str = "integrations"
    PAGINATION_LIMIT: int = 100

    @logging.trace
    async def find_integrations(self, *, name: str | None = None) -> list[dict[str, Any]]:
        """Search for integration instances with automatic pagination.

        Paginates by name since integration instance names are unique and
        enforced by the platform.

        Args:
            name: Optional instance name to filter results. If None, all
                integration instances are returned.

        Returns:
            A list of integration instance dictionaries. Returns an empty list
            if no matching instances are found.

        Raises:
            AsyncPlatformError: If any API request fails during retrieval
        """
        limit = self.PAGINATION_LIMIT
        params: dict[str, Any] = {"limit": limit, "sort": "name", "order": 1}

        if name is not None:
            params.update({"equalsField": "name", "equals": name})

        res = await self.get("/integrations", params=params)
        json_data = res.json()

        total = json_data.get("total", 0)

        logging.info(f"Found {total} integration instance(s)")

        if total == 0:
            return []

        results = json_data.get("integrations", [])

        if total <= limit:
            return results

        tasks = [
            self.get(
                "/integrations",
                params={"limit": min(limit, total - skip), "skip": skip, **params},
            )
            for skip in range(limit, total, limit)
        ]

        task_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in task_results:
            if isinstance(result, Exception):
                raise result
            results.extend(result.json().get("integrations", []))  # type: ignore[union-attr]

        return results

    @logging.trace
    async def get_integration(self, name: str) -> dict[str, Any]:
        """Retrieve a single integration instance by name.

        Args:
            name: The name of the integration instance to retrieve

        Returns:
            A dictionary containing the integration instance data including
            metadata (isActive, activeSync) and data (type, properties)

        Raises:
            AsyncPlatformError: If the API request fails or instance does not exist
        """
        res = await self.get(f"/integrations/{name}")
        return res.json()

    @logging.trace
    async def create_integration(
        self,
        *,
        name: str,
        type: str,
        properties: Mapping[str, Any],
        virtual: bool | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Create an integration instance.

        Args:
            name: Name for the new integration instance
            type: The integration adapter type
            properties: Configuration properties for the integration
            virtual: Whether to create a virtual integration. If None, the
                platform default is used.
            model: Optional integration model name to associate with the instance

        Returns:
            A dictionary containing the created integration instance data

        Raises:
            AsyncPlatformError: If an integration instance with the same name
                already exists, or if the API request fails
        """
        existing = await self.find_integrations(name=name)
        if existing:
            raise AsyncPlatformError(
                f"Integration instance `{name}` already exists"
            )

        body: dict[str, Any] = {"name": name, "type": type, "properties": dict(properties)}

        if virtual is not None:
            body["virtual"] = virtual
        if model is not None:
            body["model"] = model

        res = await self.post("/integrations", json=body)
        json_data = res.json()

        logging.info(json_data.get("message", f"Integration instance created: {name}"))

        return json_data.get("data", json_data)

    @logging.trace
    async def delete_integration(self, name: str) -> dict[str, Any]:
        """Delete an integration instance by name.

        Permanently removes an integration instance from the platform. This
        operation cannot be undone.

        Args:
            name: The name of the integration instance to delete

        Returns:
            A dictionary containing the deletion result

        Raises:
            AsyncPlatformError: If the deletion request fails
        """
        res = await self.delete(
            f"/integrations/{name}",
            expected_status=HTTPStatus.OK,
        )
        json_data = res.json()

        logging.info(f"Successfully deleted integration instance: {name}")

        return json_data

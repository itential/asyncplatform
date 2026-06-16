# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import asyncio
import json

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from collections.abc import Mapping

from asyncplatform import logging
from asyncplatform.exceptions import AsyncPlatformError
from asyncplatform.http import HTTPStatus
from asyncplatform.services import ServiceBase

_MAX_SPEC_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB


class Service(ServiceBase):
    """Service class for managing integration models in Itential Platform.

    Provides methods for interacting with integration model resources,
    including searching, retrieving, creating, updating, and deleting models.
    Integration models are imported OpenAPI 3.x specifications that define
    how the platform communicates with external systems.

    Attributes:
        name: Service identifier for logging and identification
        PAGINATION_LIMIT: Number of items to fetch per page
    """

    name: str = "integration_models"
    PAGINATION_LIMIT: int = 100

    @logging.trace
    async def find_integration_models(self, *, name: str | None = None) -> list[dict[str, Any]]:
        """Search for integration models with automatic pagination.

        Queries the platform for integration models matching the specified
        criteria. Paginates by name to ensure consistent ordering since name
        is guaranteed unique for integration models.

        Args:
            name: Optional model name to search for using exact match. If None,
                all integration models are returned.

        Returns:
            A list of integration model dictionaries. Each entry includes model,
            versionId, description, and properties. Returns an empty list if no
            matching models are found.

        Raises:
            AsyncPlatformError: If any API request fails during retrieval
        """
        limit = self.PAGINATION_LIMIT
        params: dict[str, Any] = {"limit": limit, "sort": "name", "order": 1}

        if name is not None:
            params.update({"equalsField": "name", "equals": name})

        res = await self.get("/integration-models", params=params)
        json_data = res.json()

        total = json_data.get("total", 0)

        logging.info(f"Found {total} integration model(s)")

        if total == 0:
            return []

        results = json_data.get("integrationModels", [])

        if total <= limit:
            return results

        tasks = [
            self.get(
                "/integration-models",
                params={"limit": min(limit, total - skip), "skip": skip, **params},
            )
            for skip in range(limit, total, limit)
        ]

        task_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in task_results:
            if isinstance(result, Exception):
                raise result
            results.extend(result.json().get("integrationModels", []))  # type: ignore[union-attr]

        return results

    @logging.trace
    async def create_integration_model(self, spec: Mapping[str, Any]) -> dict[str, Any]:
        """Create an integration model from an OpenAPI spec.

        Validates the spec size and checks for an existing model with the same
        version identifier before posting. The spec must be a valid OpenAPI 3.x
        document.

        Args:
            spec: A mapping containing a valid OpenAPI 3.x specification

        Returns:
            A dictionary containing the created integration model data

        Raises:
            AsyncPlatformError: If the spec exceeds 15 MB, if a model with the
                same version identifier already exists, or if the API request fails
        """
        title = spec["info"]["title"]
        version = spec["info"]["version"]
        version_id = f"{title}:{version}"

        existing = await self.find_integration_models(name=version_id)
        if existing:
            raise AsyncPlatformError(
                f"Integration model `{version_id}` already exists"
            )

        spec_size = len(json.dumps(spec).encode("utf-8"))

        if spec_size >= _MAX_SPEC_SIZE_BYTES:
            size_mb = spec_size / (1024 * 1024)
            raise AsyncPlatformError(
                f"Spec size {size_mb:.2f} MB exceeds the 15 MB limit"
            )

        res = await self.post("/integration-models", json={"model": spec})
        json_data = res.json()

        logging.info(json_data.get("message", "Integration model created"))

        return json_data.get("data", {})

    @logging.trace
    async def get_integration_model(self, name: str) -> dict[str, Any]:
        """Retrieve a single integration model by name.

        Args:
            name: The name of the integration model to retrieve

        Returns:
            A dictionary containing the integration model data including
            model, versionId, description, and properties

        Raises:
            AsyncPlatformError: If the API request fails or model does not exist
        """
        res = await self.get(f"/integration-models/{name}")
        return res.json()

    @logging.trace
    async def update_integration_model(self, spec: Mapping[str, Any]) -> dict[str, Any]:
        """Update an existing integration model with a new OpenAPI spec.

        Replaces the existing model in-place. The spec must identify the
        target model via its title and version fields. Validates spec size
        before sending to avoid platform rejections.

        Args:
            spec: A mapping containing a valid OpenAPI 3.x specification

        Returns:
            A dictionary containing the updated integration model data

        Raises:
            AsyncPlatformError: If the spec exceeds 15 MB or the API request fails
        """
        spec_size = len(json.dumps(spec).encode("utf-8"))

        if spec_size >= _MAX_SPEC_SIZE_BYTES:
            size_mb = spec_size / (1024 * 1024)
            raise AsyncPlatformError(
                f"Spec size {size_mb:.2f} MB exceeds the 15 MB limit"
            )

        res = await self.put("/integration-models", json={"model": spec})
        json_data = res.json()

        logging.info(json_data.get("message", "Integration model updated"))

        return json_data.get("data", {})

    @logging.trace
    async def delete_integration_model(self, name: str) -> dict[str, Any]:
        """Delete an integration model by name.

        Permanently removes an integration model from the platform. This
        operation cannot be undone.

        Args:
            name: The name of the integration model to delete

        Returns:
            A dictionary containing the deletion result

        Raises:
            AsyncPlatformError: If the deletion request fails
        """
        res = await self.delete(
            f"/integration-models/{name}",
            expected_status=HTTPStatus.OK,
        )
        json_data = res.json()

        logging.info(f"Successfully deleted integration model: {name}")

        return json_data

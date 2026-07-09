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
from asyncplatform.http import HTTPStatus
from asyncplatform.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing agent projects and agents in Itential Platform.

    The Service provides methods for interacting with the agent projects service,
    including importing/exporting projects. All methods
    support automatic pagination to handle large datasets efficiently.

    Attributes:
        name: Service identifier for logging and identification
        PAGINATION_LIMIT: Number of items to fetch per page when retrieving all items
    """

    name: str = "agent_projects"

    async def _get(
        self,
        endpoint: str,
        params: dict[str, Any],
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Common pagination helper for fetching all results from a paginated endpoint.

        This method handles fetching all pages of results concurrently when the total
        exceeds the page limit. It makes an initial request to determine the total count,
        then creates concurrent tasks for remaining pages.

        Args:
            endpoint: The API endpoint path to query
            params: Query parameters to include in the request
            limit: Maximum number of results per page (default: 100)

        Raises:
            Exception: Re-raises any exceptions encountered during concurrent requests
        """
        # Set pagination parameters
        params.update({"skip": 0, "limit": limit})

        # Make initial request to get total count and first page
        res = await self.get(endpoint, params=params)
        json_data = res.json()

        total = json_data["total"]

        # Handle empty results
        if total == 0:
            return []

        # If all results fit in first page, return immediately
        if total <= limit:
            return json_data["results"]

        # Start with first page results
        results = json_data["results"]

        # Create tasks for remaining pages
        tasks = []
        for skip in range(limit, total, limit):
            page_params = params.copy()
            page_params.update({"limit": limit, "skip": skip})

            tasks.append(self.get(endpoint, params=page_params))

        # Fetch all remaining pages concurrently
        if tasks:
            task_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check for exceptions in results
            for result in task_results:
                if isinstance(result, Exception):
                    raise result

            # Combine all page results (mypy doesn't understand the exception check above)
            for result in task_results:
                results.extend(result.json()["results"])  # type: ignore[union-attr]

        return results

    @logging.trace
    async def describe_agent_project(self, project_id: str) -> dict[str, Any] | None:
        """Retrieve detailed information about a specific Agent project.

        Fetches comprehensive project details including metadata, configuration,
        members, and associated agents by project ID.

        Args:
            project_id: The unique identifier (_id) of the project to retrieve

        Returns:
            A dictionary containing the complete project data, or None if the
            project does not exist

        Raises:
            HTTPError: If the API request fails
        """
        res = await self.get(f"/agent-project-service/projects/{project_id}")

        json_data = res.json()

        if "data" not in json_data:
            return None

        return json_data["data"]

    @logging.trace
    async def get_agent_projects(self) -> list[Mapping[str, Any]]:
        """Retrieve all Agent Projects projects from the Itential Platform.

        This method retrieves all projects with automatic pagination handling.
        If the total number of projects exceeds the initial limit, additional
        concurrent requests are made to fetch all remaining projects efficiently.

        Returns:
            TBD
            Returns an empty list if no projects exist.

        Raises:
            HTTPError: If any API request fails during project retrieval
        """

        limit = 100

        res = await self.get("/agent-project-service/projects", params={"limit": limit})
        data = res.json()["data"]

        total = data["metadata"]["total"]

        if total == 0:
            return []

        if total <= limit:
            return data["items"]

        tasks = []
        results = data["items"]

        for skip in range(limit, total, limit):
            remaining = total - skip
            fetch_limit = min(limit, remaining)

            tasks.append(
                self.get(
                    "/agent-project-service/projects",
                    params={"limit": fetch_limit, "skip": skip},
                )
            )

        if tasks:
            task_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in task_results:
                if isinstance(result, Exception):
                    raise result
                results.extend(result.json()["data"]["items"])  # type: ignore[union-attr]

        return results

    @logging.trace
    async def delete_agent_project(self, project_id: str) -> dict[str, Any]:
        """Delete an agent project by its ID.

        Args:
            id: The unique identifier (_id) of the agent project to delete.

        Returns:
            A dictionary containing the deletion result with the following structure:
                - message: Success message string
                - data: None
                - metadata: Dictionary containing 'deletedComponents' list with
                  information about all deleted workflows and components

        Raises:
            AsyncPlatformError: If the delete request fails.
        """
        res = await self.delete(f"/agent-project-service/projects/{project_id}")
        return res.json()

    @logging.trace
    async def patch_agent_project(self, project_id: str, data: dict[str, Any]) -> Any:
        """Update specific fields of an Agent project.

        Performs a partial update (PATCH) on a project, modifying only the
        fields specified in the data parameter without affecting other fields.

        Args:
            project_id: The unique identifier (_id) of the project to update
            data: A dictionary containing the fields to update with their new values.
                Common fields include 'name', 'description', 'members', etc.

        Returns:
            The HTTP response object from the patch operation

        Raises:
            HTTPError: If the update request fails or project doesn't exist
        """
        return await self.patch(f"/agent-project-service/projects/{project_id}", json=data)

    @logging.trace
    async def find_agent_projects(self, *, name: str | None = None) -> list[dict[str, Any]]:
        """Search for Agent projects by name.

        Queries the platform for projects matching the specified criteria. If no
        name is provided, returns all projects without filtering.

        Args:
            name: Optional project name to search for using exact match. If None,
                no name filtering is applied

        Returns:
            A list of project dictionaries matching the search criteria. Returns
            an empty list if no matching projects are found.

        Raises:
            HTTPError: If the API request fails
        """

        res = await self.get("/agent-project-service/projects")

        json_data = res.json()["data"]

        logging.info(f"Found {json_data['metadata']['total']} project(s)")

        found = json_data["items"]
        if name is None:
            return found

        for proj in found:
            if proj["name"] == name:
                return [proj]

        return []

    @logging.trace
    async def import_agent_project(
        self,
        bundle: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """Import a project into Agent Projects.

        Imports a project configuration into the Itential Platform. The import
        uses "replace" and replaces any existing projects in-place without changing
        the name and uuid.

        Args:
            bundle: A mapping containing the complete project definition including
                name, description, workflows, and other project components

        Returns:
            A mapping containing the imported project data, including the newly
            assigned project ID (_id) and complete project configuration

        Raises:
            HTTPError: If the import request fails or the project format is invalid
        """

        provider_resolutions = {
            agent["_id"]: {"profileName": "anthropic", "modelName": "claude-sonnet-4-6"}
            for agent in bundle["agents"]
        }

        res = await self.post(
            "/agent-project-service/project-bundles/import",
            json={
                "bundle": bundle,
                "conflictMode": "replace",
                "providerResolutions": provider_resolutions,
            },
            expected_status=HTTPStatus.OK,
        )

        json_data = res.json()

        projectid = json_data["data"]["_id"]

        logging.info(f"Successfully imported project {bundle['name']} (id: {projectid})")

        return json_data["data"]

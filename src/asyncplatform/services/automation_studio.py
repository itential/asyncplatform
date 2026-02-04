# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from collections.abc import Mapping

from asyncplatform import exceptions
from asyncplatform import logging
from asyncplatform.http import HTTPStatus
from asyncplatform.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing Automation Studio workflows in Itential Platform.

    The Service provides methods for interacting with Automation Studio
    workflows, including retrieving workflow details and metadata. Workflows are
    the core automation processes in Itential Platform that define executable
    processes for orchestrating network operations, device management, and
    service provisioning.

    This service handles workflow discovery across both global space and project
    namespaces, providing unified access to workflow resources regardless of
    their organizational scope.

    Inherits from ServiceBase and implements the required describe method for
    retrieving detailed workflow information by unique identifier.

    Args:
        client: An AsyncPlatform client instance for communicating with
            the Itential Platform Automation Studio API

    Attributes:
        client (AsyncPlatform): The platform client used for API communication
        name (str): Service identifier for logging and identification
    """

    name: str = "automation_studio"

    @logging.trace
    async def get_projects(self) -> list[Mapping[str, Any]]:
        """Retrieve all Automation Studio projects from the Itential Platform.

        This method retrieves all projects with automatic pagination handling.
        If the total number of projects exceeds the initial limit, additional
        concurrent requests are made to fetch all remaining projects efficiently.

        Returns:
            A list of project dictionaries containing project metadata and
            configuration. Returns an empty list if no projects exist.

        Raises:
            HTTPError: If any API request fails during project retrieval
        """
        limit = 100

        res = await self.get("/automation-studio/projects", params={"limit": limit})

        total = res["metadata"]["total"]

        if total == 0:
            return []

        if total <= limit:
            return res["data"]

        tasks = []
        results = res["data"]

        for skip in range(limit, total, limit):
            remaining = total - skip
            fetch_limit = min(limit, remaining)

            tasks.append(
                self.get(
                    "/automation-studio/projects",
                    params={"limit": fetch_limit, "skip": skip},
                )
            )

        if tasks:
            task_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in task_results:
                if isinstance(result, Exception):
                    raise result
                results.extend(result["data"])  # type: ignore[index]

        return results

    @logging.trace
    async def describe_project(self, project_id: str) -> dict[str, Any] | None:
        """Retrieve detailed information about a specific Automation Studio project.

        Fetches comprehensive project details including metadata, configuration,
        members, and associated workflows by project ID.

        Args:
            project_id: The unique identifier (_id) of the project to retrieve

        Returns:
            A dictionary containing the complete project data, or None if the
            project does not exist or the metadata count is not 1

        Raises:
            HTTPError: If the API request fails
        """
        res = await self.get(f"/automation-studio/projects/{project_id}")

        json_data = res.json()

        if json_data.get("metadata", {}).get("total") != 1:
            return None

        return json_data["data"][0]

    @logging.trace
    async def find_projects(self, *, name: str | None = None) -> list[dict[str, Any]]:
        """Search for Automation Studio projects by name.

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
        params = {}

        if name is not None:
            params["equals[name]"] = name

        res = await self.get("/automation-studio/projects", params=params)

        json_data = res.json()

        logging.info(f"Found {json_data['metadata']['total']} project(s)")

        return json_data["data"]

    @logging.trace
    async def import_project(
        self,
        project: Mapping[str, Any],
        *,
        skip_reference_validation: bool = False,
    ) -> Mapping[str, Any]:
        """Import a project into Automation Studio.

        Imports a project configuration into the Itential Platform. The import
        uses "insert-new" conflict mode and does not assign new references to
        existing components.

        Args:
            project: A mapping containing the complete project definition including
                name, description, workflows, and other project components
            skip_reference_validation: If True, skips validation of references during
                import. Defaults to False.

        Returns:
            A mapping containing the imported project data, including the newly
            assigned project ID (_id) and complete project configuration

        Raises:
            HTTPError: If the import request fails or the project format is invalid
        """
        res = await self.post(
            "/automation-studio/projects/import",
            json={
                "project": project,
                "assignNewReferences": False,
                "conflictMode": "insert-new",
                "skipReferenceValidation": skip_reference_validation,
            },
            expected_status=HTTPStatus.OK,
        )

        json_data = res.json()

        name = json_data["data"]["name"]
        projectid = json_data["data"]["_id"]

        logging.info(f"Successfully imported project {name} (id: {projectid})")

        return json_data["data"]

    @logging.trace
    async def delete_project(self, project_id: str) -> dict[str, Any]:
        """Delete an Automation Studio project by ID.

        Permanently removes a project and all its associated components from the
        platform. This operation cannot be undone.

        Args:
            project_id: The unique identifier (_id) of the project to delete

        Returns:
            A dictionary containing the deletion result with the following structure:
                - message: Success message string
                - data: None
                - metadata: Dictionary containing 'deletedComponents' list with
                  information about all deleted workflows and components

        Raises:
            HTTPError: If the deletion request fails or project doesn't exist
        """
        res = await self.delete(f"/automation-studio/projects/{project_id}")
        return res.json()

    @logging.trace
    async def patch_project(self, project_id: str, data: dict[str, Any]) -> Any:
        """Update specific fields of an Automation Studio project.

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
        return await self.patch(f"/automation-studio/projects/{project_id}", json=data)

    @logging.trace
    async def describe_workflow(self, workflow_id: str) -> Mapping[str, Any]:
        """Describe an Automation Studio workflow by ID.

        This method will attempt to get the specified workflow from the
        server and return it to the calling function as a Python dict
        object. If the workflow does not exist on the server, this method
        will raise an exception.

        This method searches for the workflow using the unique id field.
        It will find the workflow regardless of whether it is in global
        space or in a project.

        Args:
            workflow_id: The unique identifier for the workflow to retrieve

        Returns:
            A mapping containing the complete workflow data including workflow
            definition, metadata, tasks, and configuration

        Raises:
            NotFoundError: If the workflow could not be found on the server
        """
        res = await self.get(
            "/automation-studio/workflows", params={"equals[_id]": workflow_id}
        )

        data = res.json()

        if data["total"] != 1:
            msg = f"workflow id {workflow_id} not found"
            raise exceptions.NotFoundError(msg)

        return data["items"][0]

    @logging.trace
    async def find_workflows(
        self,
        *,
        name: str | None = None,
        include: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for Automation Studio workflows by name or other criteria.

        Queries the platform for workflows matching the specified criteria. If no
        parameters are provided, returns all workflows without filtering.

        Args:
            name: Optional workflow name to search for using exact match. If None,
                no name filtering is applied
            include: Optional fields to include in the response

        Returns:
            A list of workflow dictionaries matching the search criteria. Returns
            an empty list if no matching workflows are found.

        Raises:
            HTTPError: If the API request fails
        """
        params = {}

        if name is not None:
            params["equals[name]"] = name
        if include is not None:
            params["include"] = include

        res = await self.get("/automation-studio/workflows", params=params)

        return res.json()["items"]

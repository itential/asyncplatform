# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Project resource for managing Itential Platform Automation Studio projects.

This module provides the Resource class for high-level project management
operations including importing projects with member assignments, deleting
projects, and managing project access control through groups and accounts.
"""

from __future__ import annotations

import copy

from typing import TYPE_CHECKING
from typing import Any

from asyncplatform import exceptions
from asyncplatform import logging
from asyncplatform.resources import ResourceBase

if TYPE_CHECKING:
    from asyncplatform.client import Client
    from asyncplatform.models.projects import ProjectMember


class Resource(ResourceBase):
    """Resource class for managing Automation Studio projects.

    This resource provides high-level operations for project management including
    importing projects with member assignments and deleting projects by name.
    It integrates with both the Automation Studio service and the Authorization
    service to handle project membership.

    Attributes:
        studio: Property that returns the Automation Studio service instance
        authorization: Property that returns the Authorization service instance
    """

    name: str = "projects"

    def __init__(self, client: Client) -> None:
        """Initialize the project resource with a client instance.

        Args:
            client: The AsyncPlatform client instance providing API access
        """
        super().__init__(client)

    async def _ensure_project_is_new(self, name: str) -> None:
        """Ensure that a project with the given name does not exist.

        Args:
            name: The project name to check

        Raises:
            AsyncPlatformError: If a project with the name already exists
            HTTPError: If the API request fails
        """
        projects = await self.studio.find_projects(name=name)
        if projects:
            raise exceptions.AsyncPlatformError(f"Project `{name}` already exists")

    async def _resolve_member_reference(
        self,
        member: ProjectMember,
        all_groups: dict[str, dict[str, Any]],
        all_accounts: dict[str, dict[str, Any]],
    ) -> tuple[str, str]:
        """Resolve a member to its reference ID and display name.

        Looks up the member in the appropriate collection (groups or accounts)
        and returns the reference ID needed for project membership.

        Args:
            member: The ProjectMember to resolve
            all_groups: Dictionary mapping group names to group data
            all_accounts: Dictionary mapping usernames to account data

        Returns:
            A tuple containing (reference_id, display_name) where reference_id
            is the internal ID used for the member reference and display_name
            is the human-readable identifier (group name or username)

        Raises:
            AsyncPlatformError: If the member does not exist or has an
                invalid type
        """
        if member.type == "group":
            if member.name not in all_groups:
                raise exceptions.AsyncPlatformError(
                    f"Group `{member.name}` does not exist on destination server"
                )
            return all_groups[member.name]["_id"], member.name

        if member.type == "account":
            if member.username not in all_accounts:
                raise exceptions.AsyncPlatformError(
                    f"Account `{member.username}` does not exist on destination server"
                )
            return all_accounts[member.username]["_id"], member.username

        raise exceptions.AsyncPlatformError(
            f"Invalid member type `{member.type}`, must be 'group' or 'account'"
        )

    async def _update_project_members(
        self,
        project: dict[str, Any],
        members: list[ProjectMember],
        *,
        preserve_existing_members: bool = True,
    ) -> None:
        """Update project members by adding new members to the project.

        Resolves member references, checks for duplicates, and updates the
        project with the new member list if any members were added.

        Args:
            project: The project data from the import response
            members: List of ProjectMembers to add to the project
            preserve_existing_members: If True (default), adds to existing
                members. If False, clears existing members before adding

        Raises:
            AsyncPlatformError: If any member does not exist or has an
                invalid type
            HTTPError: If the patch operation fails
        """
        project_id = project["_id"]

        if not preserve_existing_members:
            project["members"] = []

        # Fetch all groups and accounts once
        all_groups = await self.get_groups()
        all_accounts = await self.get_accounts()

        # Get existing members
        project_members = list(project.get("members", []))
        existing_member_refs = {member["reference"] for member in project_members}

        members_added = False

        # Process each new member
        for member in members:
            ref_id, member_name = await self._resolve_member_reference(
                member, all_groups, all_accounts
            )

            if ref_id not in existing_member_refs:
                member_dict = member.asdict()
                member_dict["reference"] = ref_id
                project_members.append(member_dict)
                members_added = True
            else:
                logging.warning(f"Project member `{member_name}` already exists")

        # Update project if members were added
        if members_added:
            await self.studio.patch_project(project_id, {"members": project_members})

    @logging.trace
    async def importer(
        self,
        project: dict[str, Any],
        *,
        members: list[ProjectMember] | None = None,
        preserve_existing_members: bool = True,
        overwrite: bool = False,
        skip_reference_validation: bool = False,
    ) -> dict[str, Any]:
        """Import a project into the platform with optional member assignments.

        Imports a project and optionally assigns specified groups or user accounts
        as project members. By default, validates that the project doesn't already
        exist. Can optionally overwrite an existing project.

        Args:
            project: Complete project definition including name, description,
                workflows, and other components. Must include a 'name' field
            members: Optional list of ProjectMember objects specifying groups
                or accounts to add as project members. Each member is validated
                to exist before being added
            preserve_existing_members: If True (default), retains any members
                that were included in the imported project definition. If False,
                removes all members from the imported project before adding the
                specified members list
            overwrite: If True, overwrites the project if it already exists in
                the target environment. If False (default), raises an error if
                the project already exists
            skip_reference_validation: If True, skips validation of references
                during import. Defaults to False.

        Returns:
            The imported project data including _id, name, and complete
            configuration from the initial import response

        Raises:
            AsyncPlatformError: If overwrite is False and a project with the
                same name already exists, or if any specified member (group or
                account) does not exist, or if a member has an invalid type
            HTTPError: If the import or patch operations fail
        """
        project = copy.deepcopy(project)

        # Check if project exists and handle based on overwrite flag
        if not overwrite:
            await self._ensure_project_is_new(project["name"])
        else:
            # Delete existing project if overwrite is True
            existing_projects = await self.studio.find_projects(name=project["name"])
            if existing_projects:
                await self.studio.delete_project(existing_projects[0]["_id"])

        # Import the project
        result = await self.studio.import_project(
            project, skip_reference_validation=skip_reference_validation
        )

        # Add members if specified
        if members:
            await self._update_project_members(
                result, members, preserve_existing_members=preserve_existing_members
            )

        return result

    @logging.trace
    async def delete(self, name: str) -> dict[str, Any]:
        """Delete a project by name.

        Searches for a project by name and deletes it if found. This is a
        convenience method that wraps find and delete operations.

        Args:
            name: The name of the project to delete

        Returns:
            A dictionary containing the deletion result including 'message',
            'data', and 'metadata' fields with information about deleted
            components. Returns an empty dictionary if no project with the
            specified name is found.

        Raises:
            HTTPError: If the find or delete operations fail
        """
        projects = await self.studio.find_projects(name=name)
        if not projects:
            return {}

        return await self.studio.delete_project(projects[0]["_id"])

    @logging.trace
    async def set_members(
        self,
        project_name: str,
        members: list[ProjectMember],
        *,
        preserve_existing_members: bool = True,
    ) -> dict[str, Any]:
        """Set or update project members.

        Adds the specified members to a project, optionally preserving or
        replacing all existing members. Members are validated to ensure they
        exist in the platform before being added.

        Args:
            project_name: The name of the project to update
            members: List of ProjectMember objects to add to the project
            preserve_existing_members: If True (default), adds members to the
                existing list. If False, removes all existing members before
                adding new ones

        Returns:
            The project data after member updates, or None if
            preserve_existing_members=False and no members are added

        Raises:
            AsyncPlatformError: If the project cannot be uniquely identified
                by name (zero or multiple matches), or if any member does not
                exist or has an invalid type
            HTTPError: If the find or patch operations fail
        """
        projects = await self.studio.find_projects(name=project_name)

        if len(projects) != 1:
            raise exceptions.AsyncPlatformError(
                f"Could not uniquely identify project {project_name}"
            )

        project = projects[0]

        await self._update_project_members(
            project, members, preserve_existing_members=preserve_existing_members
        )

        return project

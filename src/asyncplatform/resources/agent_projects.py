# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Resource for managing Itential Platform Agent projects."""

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
    """Resource class for managing Agent projects."""

    name: str = "agent_projects"

    def __init__(self, client: Client) -> None:
        """Initialize the agent projects resource with a client instance.

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
        projects = await self.agent_projects.find_agent_projects(name=name)
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
            A tuple of (reference_id, display_name) where reference_id
            is the internal ID used for the member reference and display_name
            is the human-readable identifier (group name or username)

        Raises:
            AsyncPlatformError: If the member does not exist or has an invalid type
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
    ) -> dict[str, Any] | None:
        """Update project members, optionally preserving existing ones.

        Resolves member references and updates the project with the new member
        list. When preserve_existing_members is True, existing members from the
        project are appended to the incoming list before resolving.

        Args:
            project: The project data containing at minimum '_id' and 'members'
            members: List of ProjectMembers to add to the project
            preserve_existing_members: If True (default), existing project
                members are kept alongside the new ones.

        Raises:
            AsyncPlatformError: If any member does not exist or has an invalid type
            HTTPError: If the patch operation fails
        """
        project_id = project["_id"]

        if preserve_existing_members:
            members.extend(
                ProjectMember(
                    name=member.get("name"),
                    username=member.get("username"),
                    type=member["type"],
                    role=member["role"],
                )
                for member in project.get("members", [])
            )

        all_groups = await self.get_groups()
        all_accounts = await self.get_accounts()

        project_members = []

        for member in members:
            ref_id, _ = await self._resolve_member_reference(
                member, all_groups, all_accounts
            )

            member_dict = {
                "type": member.type,
                "role": member.role,
                "reference": ref_id,
            }
            project_members.append(member_dict)

        if project_members:
            res = await self.agent_projects.patch_agent_project(
                project_id, {"members": project_members}
            )
            return res.json()["data"]

        return None

    @logging.trace
    async def importer(
        self,
        bundle: dict[str, Any],
        *,
        members: list[ProjectMember] | None = None,
        overwrite: bool = False,
        preserve_existing_members: bool = True,
    ) -> dict[str, Any]:
        """Import an agent project bundle into the platform.

        Imports a bundle using given overwrite value and optionally assigns
        members to the project after import. The import response itself does
        not include the project's prior members, so when preserve_existing_members
        is requested, the existing project is fetched via a GET before it is
        overwritten so its real member list can be carried forward.

        Args:
            bundle: Complete agent project bundle including agents and configuration
            members: Optional list of ProjectMember objects to assign to the project
            overwrite: If true, deletes project and then reimports. If false (default)
            raises an error if the project already exists
            preserve_existing_members: If True (default), members already on an
                existing project (when overwrite is True) are kept alongside
                members. Matches the Studio Projects importer's default.

        Returns:
            The imported project data including _id and name

        Raises:
            AsyncPlatformError: If any specified member does not exist or has an
                invalid type
            HTTPError: If the import or patch operations fail
        """
        project = copy.deepcopy(bundle)

        members = list(members) if members else []

        # Check if project exists and handle based on overwrite flag
        if not overwrite:
            await self._ensure_project_is_new(project["name"])
        else:
            # Delete existing project if overwrite is True
            existing_projects = await self.agent_projects.find_agent_projects(
                name=project["name"]
            )
            if existing_projects:
                if preserve_existing_members:
                    members.extend(
                        ProjectMember(
                            name=member.get("name"),
                            username=member.get("username"),
                            type=member["type"],
                            role=member["role"],
                        )
                        for member in existing_projects[0].get("members", [])
                    )
                await self.agent_projects.delete_agent_project(
                    existing_projects[0]["_id"]
                )

        # Import the project
        result = await self.agent_projects.import_agent_project(project)

        # Add members if any were specified or carried forward
        if members:
            await self._update_project_members(result, members)

        return result

    @logging.trace
    async def set_members(
        self,
        project_name: str,
        members: list[ProjectMember],
        *,
        preserve_existing_members: bool = True,
    ) -> dict[str, Any] | None:
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
        projects = await self.agent_projects.find_agent_projects(name=project_name)

        if len(projects) != 1:
            raise exceptions.AsyncPlatformError(
                f"Could not uniquely identify project {project_name}"
            )

        project = projects[0]

        return await self._update_project_members(
            project, members, preserve_existing_members=preserve_existing_members
        )

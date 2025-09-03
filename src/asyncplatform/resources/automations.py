# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Automation resource for managing Itential Platform Operations Manager automations.

This module provides the Resource class for high-level automation management
operations including importing automations, deleting automations, and checking
automation existence in the Operations Manager service.
"""

from __future__ import annotations

import copy

from typing import Any

from asyncplatform import exceptions
from asyncplatform import logging
from asyncplatform.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing Operations Manager automations.

    This resource provides high-level operations for automation management
    including importing automations with validation and deleting automations
    by name. It integrates with both the Operations Manager service and the
    Automation Studio service to handle automation lifecycle operations.

    Attributes:
        operations_manager: Property that returns the Operations Manager
            service instance
        studio: Property that returns the Automation Studio service instance
    """

    name: str = "automations"

    async def _check_if_automation_exists(self, name: str) -> bool:
        """Check if an automation with the given name exists in Operations Manager.

        Args:
            name: The automation name to search for

        Returns:
            True if at least one automation with the specified name exists,
            False otherwise

        Raises:
            HTTPError: If the API request fails
        """
        automations = await self.operations_manager.find_automations(name=name)
        return any(automation["name"] == name for automation in automations)

    async def _validate_gbac(
        self,
        gbac: dict[str, list[dict[str, Any]]],
        all_groups: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Validate that all GBAC groups exist in the destination server.

        Checks both read and write groups in the GBAC configuration against
        the available groups on the destination server.

        Args:
            gbac: GBAC configuration containing 'read' and 'write' group lists
            all_groups: Dictionary mapping group names to group data

        Returns:
            List of group dictionaries that are missing from the destination server
        """
        source_names = set(all_groups.keys())
        groups_to_check = gbac["write"] + gbac["read"]
        return [
            group
            for group in groups_to_check
            if group["name"] not in source_names
        ]

    async def _is_workflow(self, automation: dict[str, Any]) -> None:
        """Validate that the automation has the correct component type.

        Args:
            automation: The automation configuration to validate

        Raises:
            AsyncPlatformError: If componentType is not 'workflows'
        """
        component_type = automation.get("componentType")
        if component_type != "workflows":
            msg = (
                f"Invalid automation type, expected `workflows`, "
                f"got `{component_type}`"
            )
            raise exceptions.AsyncPlatformError(msg)

    async def _ensure_automation_is_new(self, name: str) -> None:
        """Ensure that an automation with the given name does not exist.

        Args:
            name: The automation name to check

        Raises:
            AsyncPlatformError: If an automation with the name already exists
            HTTPError: If the API request fails
        """
        if await self._check_if_automation_exists(name):
            raise exceptions.AsyncPlatformError(
                f"Automation `{name}` already exists"
            )

    async def _process_gbac(
        self,
        gbac: dict[str, Any],
        write_groups: list[str] | None,
        read_groups: list[str] | None,
        *,
        preserve_read_groups: bool,
        preserve_write_groups: bool,
    ) -> dict[str, Any]:
        """Process GBAC configuration for automation import.

        Creates a new GBAC configuration by processing read and write groups
        without mutating the input automation dictionary.

        Args:
            automation: The automation configuration containing GBAC settings
            write_groups: Group names to add with write access
            read_groups: Group names to add with read access
            preserve_read_groups: Whether to keep existing read groups
            preserve_write_groups: Whether to keep existing write groups

        Returns:
            A new GBAC configuration dictionary with processed groups

        Raises:
            AsyncPlatformError: If any required groups are missing from the
                destination server
        """
        # Get all groups once (cached)
        all_groups = await self.get_groups()

        # Create a new gbac dict to avoid mutating the input
        gbac = {
            "read": gbac["read"].copy() if preserve_read_groups else [],
            "write": gbac["write"].copy() if preserve_write_groups else [],
        }

        # Validate all existing groups exist on destination
        missing_groups = await self._validate_gbac(gbac, all_groups)

        if missing_groups:
            missing_names = ", ".join(g["name"] for g in missing_groups)
            raise exceptions.AsyncPlatformError(
                f"Destination server is missing groups: {missing_names}"
            )

        # Process read groups
        existing_read_names = {group["name"] for group in gbac["read"]}
        for group_name in read_groups or []:
            if group_name not in all_groups:
                raise exceptions.AsyncPlatformError(
                    f"Group `{group_name}` not found on destination server"
                )
            if group_name not in existing_read_names:
                gbac["read"].append(all_groups[group_name])
                existing_read_names.add(group_name)

        # Process write groups
        existing_write_names = {group["name"] for group in gbac["write"]}
        for group_name in write_groups or []:
            if group_name not in all_groups:
                raise exceptions.AsyncPlatformError(
                    f"Group `{group_name}` not found on destination server"
                )
            if group_name not in existing_write_names:
                gbac["write"].append(all_groups[group_name])
                existing_write_names.add(group_name)

        return gbac

    @logging.trace
    async def get_automation_by_name(self, name: str) -> dict[str, Any] | None:
        """Retrieve the automation ID for a given automation name.

        Searches for an automation by name and returns its unique identifier.
        Only returns an ID if an exact name match is found.

        Args:
            name: The automation name to search for

        Returns:
            The automation ID if found, None otherwise

        Raises:
            HTTPError: If the API request fails
        """
        automations = await self.operations_manager.find_automations(name=name)
        return next(
            (
                automation
                for automation in automations
                if automation["name"] == name
            ),
            None,
        )

    @logging.trace
    async def importer(
        self,
        automation: dict[str, Any],
        write_groups: list[str] | None = None,
        read_groups: list[str] | None = None,
        *,
        preserve_read_groups: bool = True,
        preserve_write_groups: bool = True,
    ) -> dict[str, Any]:
        """Import an automation into Operations Manager with GBAC configuration.

        Imports an automation configuration into the platform after validating
        the component type, checking for duplicates, and processing GBAC
        (Group-Based Access Control) settings. Supports both preserving
        existing groups and adding new groups for read/write access.

        Args:
            automation: Complete automation definition including name, description,
                componentName, componentType, componentId, and gbac settings.
                Must have 'componentType' set to 'workflows'
            write_groups: Group names to add with write access (optional)
            read_groups: Group names to add with read access (optional)
            preserve_read_groups: If True, keep existing read groups
                from the automation definition; if False, clear them before
                adding new ones
            preserve_write_groups: If True, keep existing write groups
                from the automation definition; if False, clear them before
                adding new ones

        Raises:
            AsyncPlatformError: If componentType is not 'workflows', if an
                automation with the same name already exists, or if any
                required groups are missing from the destination server
            HTTPError: If any API request fails
        """
        # Create a deep copy to avoid mutating the input
        automation = copy.deepcopy(automation)

        # Ensure no duplicate automation exists
        await self._ensure_automation_is_new(automation["name"])

        # Validate the automation is a workflow
        await self._is_workflow(automation)

        # Process GBAC configuration
        automation["gbac"] = await self._process_gbac(
            automation["gbac"],
            write_groups,
            read_groups,
            preserve_read_groups=preserve_read_groups,
            preserve_write_groups=preserve_write_groups
        )

        # Import the automation
        result = await self.operations_manager.import_automation(automation)

        automation_name = result["name"]
        automation_id = result["_id"]

        logging.info(
            f"Successfully imported automation {automation_name} "
            f"(id: {automation_id})"
        )

        return result

    @logging.trace
    async def delete(self, name: str) -> None:
        """Delete an automation by name.

        Searches for an automation by name and deletes it if found. This is a
        convenience method that wraps find and delete operations.

        Args:
            name: The name of the automation to delete

        Raises:
            AsyncPlatformError: If no automation with the specified name is found
                or multiple automations match the name
            HTTPError: If the find or delete operations fail
        """
        automation = await self.get_automation_by_name(name)
        if automation is not None:
            await self.operations_manager.delete_automation(automation["_id"])

    @logging.trace
    async def set_gbac(
        self,
        automation_name: str,
        read_groups: list[str] | None = None,
        write_groups: list[str] | None = None,
        *,
        preserve_read_groups: bool = True,
        preserve_write_groups: bool = True,
    ) -> dict[str, Any]:
        """Set or update GBAC configuration for an existing automation.

        Updates the Group-Based Access Control (GBAC) settings for an
        automation by name, optionally preserving or replacing existing
        read and write groups.

        Args:
            automation_name: The name of the automation to update
            read_groups: Group names to add with read access (optional)
            write_groups: Group names to add with write access (optional)
            preserve_read_groups: If True (default), adds to existing read
                groups. If False, clears existing read groups before adding
            preserve_write_groups: If True (default), adds to existing write
                groups. If False, clears existing write groups before adding

        Returns:
            The updated automation data after GBAC modifications

        Raises:
            AsyncPlatformError: If the automation cannot be uniquely identified
                by name, or if any required groups are missing
            HTTPError: If the find or update operations fail
        """
        automation = await self.get_automation_by_name(automation_name)
        if automation is None:
            raise exceptions.AsyncPlatformError(
                f"Could not find automation `{automation_name}`"
            )

        # Early return if no changes requested
        if (
            not read_groups
            and not write_groups
            and preserve_read_groups
            and preserve_write_groups
        ):
            logging.info(
                f"No GBAC changes requested for automation `{automation_name}`"
            )
            return automation

        automation["gbac"] = await self._process_gbac(
            automation["gbac"],
            write_groups,
            read_groups,
            preserve_read_groups=preserve_read_groups,
            preserve_write_groups=preserve_write_groups
        )

        result = await self.operations_manager.update_automation( automation)

        logging.info(
            f"Successfully updated GBAC for automation `{result['name']}` "
            f"(id: {result['_id']})"
        )

        return result

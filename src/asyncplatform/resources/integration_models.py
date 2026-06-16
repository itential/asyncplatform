# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Integration model resource for managing Itential Platform integration models.

This module provides the Resource class for high-level integration model
management operations including importing OpenAPI specs with delete-before-replace
semantics and deleting models by version identifier.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from asyncplatform import logging
from asyncplatform.resources import ResourceBase

if TYPE_CHECKING:
    from collections.abc import Mapping


class Resource(ResourceBase):
    """Resource class for managing integration models.

    Provides high-level lifecycle operations for integration models, wrapping
    the integration_models service with import and delete convenience methods.

    Attributes:
        integration_models: Property that returns the Integration Models
            service instance
    """

    name: str = "integration_models"

    @logging.trace
    async def importer(self, spec: Mapping[str, Any]) -> dict[str, Any]:
        """Import an integration model, replacing any existing version.

        Derives the version identifier from the spec's info block, deletes any
        existing model with the same version identifier, then creates the new
        model. Follows delete-before-replace to avoid version conflicts on
        re-import.

        Args:
            spec: A valid OpenAPI 3.x specification. Must include info.title
                and info.version fields

        Returns:
            A dictionary containing the created integration model data

        Raises:
            AsyncPlatformError: If the spec exceeds 15 MB or any API request fails
        """
        title: str = spec["info"]["title"]
        version: str = spec["info"]["version"]
        version_id = f"{title}:{version}"

        existing = await self.integration_models.find_integration_models(
            name=version_id
        )
        if existing:
            await self.integration_models.delete_integration_model(version_id)
            logging.info(f"Deleted existing integration model: {version_id}")

        result = await self.integration_models.create_integration_model(spec)

        logging.info(f"Successfully imported integration model: {version_id}")

        return result

    @logging.trace
    async def delete(self, version_id: str) -> dict[str, Any]:
        """Delete an integration model by version identifier.

        Searches for a model by version identifier and deletes it if found.
        Returns an empty dictionary if no matching model exists.

        Args:
            version_id: The version identifier of the model to delete, in the
                form title:version (e.g. "My API:1.0.0")

        Returns:
            A dictionary containing the deletion result, or an empty dictionary
            if no model with the specified version identifier was found

        Raises:
            AsyncPlatformError: If the delete operation fails
        """
        existing = await self.integration_models.find_integration_models(
            name=version_id
        )
        if not existing:
            return {}

        return await self.integration_models.delete_integration_model(version_id)

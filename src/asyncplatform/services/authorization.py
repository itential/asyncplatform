# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import asyncio

from typing import Any

from asyncplatform import logging
from asyncplatform.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing authorization groups and accounts in Itential Platform.

    The Service provides methods for interacting with the Authorization service,
    including retrieving authorization groups and user accounts. All methods
    support automatic pagination to handle large datasets efficiently.

    Attributes:
        name: Service identifier for logging and identification
    """

    name: str = "authorization"

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
    async def get_accounts(self) -> list[dict[str, Any]]:
        """Retrieve all user accounts from the authorization service.

        Fetches all active, non-service accounts using automatic pagination.
        Results are fetched concurrently for improved performance.

        Raises:
            Exception: Any errors encountered during API requests
        """
        params = {"inactive": False, "isServiceAccount": False}

        return await self._get("/authorization/accounts", params=params)

    @logging.trace
    async def get_groups(self) -> list[dict[str, Any]]:
        """Retrieve all authorization groups from the authorization service.

        Fetches all active authorization groups using automatic pagination.
        Results are fetched concurrently for improved performance.

        Raises:
            Exception: Any errors encountered during API requests
        """
        params = {"inactive": False}

        return await self._get("/authorization/groups", params=params)

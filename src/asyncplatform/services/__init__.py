# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import ipsdk

if TYPE_CHECKING:
    from asyncplatform.context import Context

from .. import exceptions
from .. import logging
from ..http import HTTPMethod
from ..http import HTTPStatus


class ServiceBase:
    """Base class for all platform API services.

    ServiceBase provides common HTTP method helpers and exception handling
    for all service implementations. Each service inherits from this class
    and has access to the shared context containing the API client.

    Attributes:
        ctx: Shared context providing access to the API client
    """

    def __init__(self, ctx: Context) -> None:
        """Initialize the service with a shared context.

        Args:
            ctx: Context object containing the API client
        """
        self.ctx = ctx

    async def _send_request(
        self,
        method: HTTPMethod,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        expected_status: HTTPStatus | None = None,
    ) -> Any:
        """Send an HTTP request to the specified path.

        This method sends an HTTP request with the specified method and parameters,
        optionally validating the response status code against an expected value.

        Args:
            method: HTTP method enum value (HTTPMethod.GET, HTTPMethod.POST, etc.)
            path: API endpoint path
            params: Optional query parameters for the request
            json: Optional JSON body for the request
            expected_status: Optional expected HTTP status code to validate

        Raises:
            AsyncPlatformError: For network, authentication, HTTP, or JSON errors
        """
        logging.info(f"{method.value} {path}")

        try:
            # Prepare request arguments
            kwargs = {}
            if params is not None:
                kwargs["params"] = params
            if json is not None:
                kwargs["json"] = json

            # Get the appropriate client method
            client_method = getattr(self.ctx.client, method.value.lower())

            res = await client_method(path, **kwargs)

            # Validate expected status if provided
            if expected_status is not None and res.status_code != expected_status:
                logging.warning(
                    f"Unexpected status code: expected {expected_status}, got {res.status_code}"
                )

            return res

        except ipsdk.exceptions.HTTPStatusError as exc:
            raise exceptions.AsyncPlatformError(str(exc)) from exc
        except ipsdk.exceptions.RequestError as exc:
            msg = f"Request error while accessing {path}: {exc!s}"
            raise exceptions.AsyncPlatformError(msg) from exc
        except Exception as exc:
            msg = f"Unexpected error during {method.value} {path}: {exc!s}"
            raise exceptions.AsyncPlatformError(msg) from exc

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        expected_status: HTTPStatus | None = None,
    ) -> Any:
        """Send a GET request to the specified path.

        Convenience method for GET requests that wraps _send_request.

        Args:
            path: API endpoint path
            params: Optional query parameters for the request
            expected_status: Optional expected HTTP status code to validate

        Raises:
            AsyncPlatformError: For network, authentication, HTTP, or JSON errors
        """
        return await self._send_request(
            HTTPMethod.GET,
            path,
            params=params,
            expected_status=(expected_status or HTTPStatus.OK),
        )

    async def post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        expected_status: HTTPStatus | None = None,
    ) -> Any:
        """Send a POST request to the specified path.

        Convenience method for POST requests that wraps _send_request.

        Args:
            path: API endpoint path
            json: Optional JSON body for the request
            params: Optional query parameters for the request
            expected_status: Optional expected HTTP status code to validate

        Raises:
            AsyncPlatformError: For network, authentication, HTTP, or JSON errors
        """
        return await self._send_request(
            HTTPMethod.POST,
            path,
            params=params,
            json=json,
            expected_status=(expected_status or HTTPStatus.CREATED)
        )

    async def put(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        expected_status: HTTPStatus | None = None,
    ) -> Any:
        """Send a PUT request to the specified path.

        Convenience method for PUT requests that wraps _send_request.

        Args:
            path: API endpoint path
            json: Optional JSON body for the request
            params: Optional query parameters for the request
            expected_status: Optional expected HTTP status code to validate

        Raises:
            AsyncPlatformError: For network, authentication, HTTP, or JSON errors
        """
        return await self._send_request(
            HTTPMethod.PUT,
            path,
            params=params,
            json=json,
            expected_status=(expected_status or HTTPStatus.OK)
        )

    async def patch(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        expected_status: HTTPStatus | None = None,
    ) -> Any:
        """Send a PATCH request to the specified path.

        Convenience method for PATCH requests that wraps _send_request.
        PATCH is typically used for partial updates to resources.

        Args:
            path: API endpoint path
            json: Optional JSON body for the request
            params: Optional query parameters for the request
            expected_status: Optional expected HTTP status code to validate

        Raises:
            AsyncPlatformError: For network, authentication, HTTP, or JSON errors
        """
        return await self._send_request(
            HTTPMethod.PATCH,
            path,
            params=params,
            json=json,
            expected_status=(expected_status or HTTPStatus.OK)
        )

    async def delete(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        expected_status: HTTPStatus | None = None,
    ) -> Any:
        """Send a DELETE request to the specified path.

        Convenience method for DELETE requests that wraps _send_request.

        Args:
            path: API endpoint path
            params: Optional query parameters for the request
            expected_status: Optional expected HTTP status code to validate

        Raises:
            AsyncPlatformError: For network, authentication, HTTP, or JSON errors
        """
        return await self._send_request(
            HTTPMethod.DELETE,
            path,
            params=params,
            expected_status=(expected_status or HTTPStatus.NO_CONTENT)
        )

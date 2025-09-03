# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""HTTP-related enumerations and utilities for the asyncplatform library.

This module provides HTTP method and status code enumerations used throughout
the asyncplatform library.

HTTPStatus is imported from the standard library's http module (available in all
supported Python versions).

For Python 3.11+, HTTPMethod is imported from the standard library's http module.
For Python 3.10 and earlier, a compatible custom implementation is provided.
"""

from __future__ import annotations

import sys

from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from ipsdk import connection

# Python 3.11+ has HTTPMethod in the standard library
if sys.version_info >= (3, 11):
    from http import HTTPMethod
else:
    from enum import Enum

    class HTTPMethod(Enum):
        """HTTP method enumeration.

        This enum provides standard HTTP methods as strings.
        Members can be compared directly with string method names.
        """

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        PATCH = "PATCH"
        DELETE = "DELETE"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"
        TRACE = "TRACE"
        CONNECT = "CONNECT"


class Response:
    """
    Wrapper class for HTTP responses that provides enhanced functionality over
    connection.Response

    The Response class wraps an connection.Response object and provides additional
    convenience methods and properties for working with API responses. It maintains
    compatibility with the underlying connection.Response while adding SDK-specific
    functionality.

    Args:
        ipsdk_response (connection.Response): The underlying ipsdk response object

    Raises:
        ValueError: If the ipsdk_response is None or invalid
    """

    def __init__(self, ipsdk_response: connection.Response) -> None:
        self._response = ipsdk_response

    @property
    def status_code(self) -> int:
        """
        Get the HTTP status code

        Returns:
            int: The HTTP status code
        """
        return self._response.status_code

    @property
    def headers(self) -> Any:
        """
        Get the response headers

        Returns:
            ipsdk.Headers: The response headers
        """
        return self._response.headers

    @property
    def content(self) -> bytes:
        """
        Get the raw response content as bytes

        Returns:
            bytes: The raw response content
        """
        return self._response.content

    @property
    def text(self) -> str:
        """
        Get the response content as text

        Returns:
            str: The response content decoded as text
        """
        return self._response.text

    @property
    def url(self) -> Any:
        """
        Get the request URL

        Returns:
            ipsdk.URL: The URL that was requested
        """
        return self._response.url

    @property
    def request(self) -> Any:
        """
        Get the original request object

        Returns:
            ipsdk.Request: The original request that generated this response
        """
        return self._response.request

    def json(self) -> dict[str, Any]:
        """
        Parse the response content as JSON

        Returns:
            dict[str, Any]: The parsed JSON response

        Raises:
            ValueError: If the response content is not valid JSON
        """
        try:
            return self._response.json()
        except Exception as exc:
            msg = f"Failed to parse response as JSON: {exc!s}"
            raise ValueError(msg)

    def raise_for_status(self) -> None:
        """
        Raise an exception if the response status indicates an error

        Raises:
            ipsdk.HTTPStatusError: If the response status code indicates an error
        """
        self._response.raise_for_status()

    def is_success(self) -> bool:
        """
        Check if the response indicates success (2xx status code)

        Returns:
            bool: True if the status code is in the 2xx range, False otherwise
        """
        return (
            HTTPStatus.OK.value
            <= self.status_code
            < HTTPStatus.MULTIPLE_CHOICES.value
        )

    def is_error(self) -> bool:
        """
        Check if the response indicates an error (4xx or 5xx status code)

        Returns:
            bool: True if the status code indicates an error, False otherwise
        """
        return self.status_code >= HTTPStatus.BAD_REQUEST.value

    def __repr__(self) -> str:
        """
        String representation of the response

        Returns:
            str: A string representation of the response
        """
        return f"Response(status_code={self.status_code}, url='{self.url}')"

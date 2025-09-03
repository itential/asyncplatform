# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from asyncplatform import logging


class AsyncPlatformError(Exception):
    """Base exception for all asyncplatform errors.

    This exception serves as the base class for all custom exceptions
    raised by the asyncplatform library. It can optionally wrap an
    underlying exception for context preservation.

    Attributes:
        message: Human-readable error message
        _exc: Optional source exception for chaining
    """

    @logging.trace
    def __init__(
        self,
        message: str,
        exc: Exception | None = None,
    ) -> None:
        """Initialize the base SDK exception.

        Args:
            message: Human-readable error message
            exc: Optional source exception for context preservation
        """
        super().__init__(message)
        self._exc = exc

    @property
    def message(self) -> str:
        """Get the error message."""
        return self.args[0]

    @logging.trace
    def __str__(self) -> str:
        """Return a string representation of the error."""
        return self.message


class NotFoundError(AsyncPlatformError):
    """Exception raised when a requested resource is not found.

    This exception is raised when attempting to retrieve a resource (such as
    a workflow, project, or other entity) that does not exist on the platform.
    """


class SerializationError(AsyncPlatformError):
    """Exception raised when JSON parsing or serialization fails.

    This exception is raised by the jsonutils module when encountering
    errors during JSON encoding or decoding operations.
    """

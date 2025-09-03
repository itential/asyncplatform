# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from . import logging

if TYPE_CHECKING:
    import ipsdk

__all__ = ("Context",)


class Context:
    """Shared context for services providing access to client.

    The Context class manages shared state between services, including the
    underlying ipsdk client connection. It handles proper cleanup of resources
    when the context is no longer needed.

    Attributes:
        client: The ipsdk AsyncPlatform client instance for API calls
    """

    def __init__(self) -> None:
        """Initialize the context with client instance."""
        self.client: ipsdk.AsyncPlatform | None = None

    @logging.trace
    async def cleanup(self) -> None:
        """Clean up resources used by this context.

        This method handles cleanup of the ipsdk client connection.
        Exceptions during cleanup are logged but not propagated to avoid
        masking primary exceptions.
        """
        if self.client:
            try:
                await self.client.close()
            except Exception as exc:
                logging.warning(f"Error closing client during cleanup: {exc!s}")

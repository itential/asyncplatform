# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Any

from asyncplatform import logging
from asyncplatform.services import ServiceBase


class Service(ServiceBase):
    name: str = "help"

    @logging.trace
    async def get_openapi(self, url: str | None = None) -> dict[str, Any]:
        """ """
        res = await self.get("/help/openapi", params={"url": (url or "/")})
        return res.json()

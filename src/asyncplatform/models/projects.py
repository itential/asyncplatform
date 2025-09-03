# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import fields
from typing import Literal


@dataclass(slots=True, kw_only=True, frozen=True)
class ProjectMember:
    """Represents a member of an Itential Platform project.

    This model encapsulates information about a user or group that has
    access to a project within the Itential Platform, including their
    role and access permissions.

    Attributes:
        username: The username of the account member (used for type="account")
        name: The name of the group member (used for type="group")
        type: The type of member ("account" or "group")
        role: The role assigned to the member. Must be one of: "owner",
            "editor", "operator", or "viewer". Defaults to "viewer".

    Example:
        ```python
        # Account member
        member = ProjectMember(
            username="john.doe",
            type="account",
            role="editor"
        )

        # Group member
        member = ProjectMember(
            name="Administrators",
            type="group",
            role="owner"
        )
        ```
    """

    username: str | None = None
    name: str | None = None
    type: str | None = None
    role: Literal["owner", "editor", "operator", "viewer"] = "viewer"

    def asdict(self) -> dict:
        """Convert the ProjectMember instance to a dictionary.

        Only includes fields that have non-None values to create a compact
        dictionary representation suitable for API requests.

        Args:
            None

        Returns:
            A dictionary containing only the non-None fields and their values

        Raises:
            None
        """
        return {
            f.name: value
            for f in fields(self)
            if (value := getattr(self, f.name)) is not None
        }

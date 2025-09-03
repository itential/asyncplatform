# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.models.projects module."""

import pytest

from asyncplatform.models.projects import ProjectMember


class TestProjectMember:
    """Test suite for ProjectMember dataclass."""

    def test_project_member_initialization_with_account(self):
        """Test creating a ProjectMember for an account.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        member = ProjectMember(
            username="john.doe",
            type="account",
            role="editor"
        )

        assert member.username == "john.doe"
        assert member.type == "account"
        assert member.role == "editor"
        assert member.name is None

    def test_project_member_initialization_with_group(self):
        """Test creating a ProjectMember for a group.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        member = ProjectMember(
            name="Administrators",
            type="group",
            role="owner"
        )

        assert member.name == "Administrators"
        assert member.type == "group"
        assert member.role == "owner"
        assert member.username is None

    def test_project_member_default_role(self):
        """Test that default role is 'viewer'.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        member = ProjectMember(username="user", type="account")

        assert member.role == "viewer"

    def test_project_member_all_roles(self):
        """Test all valid role values.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        roles = ["owner", "editor", "operator", "viewer"]

        for role in roles:
            member = ProjectMember(username="user", type="account", role=role)
            assert member.role == role

    def test_project_member_asdict_with_all_fields(self):
        """Test asdict method with all fields populated.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        member = ProjectMember(
            username="john.doe",
            name="John",
            type="account",
            role="editor"
        )

        result = member.asdict()

        assert result == {
            "username": "john.doe",
            "name": "John",
            "type": "account",
            "role": "editor"
        }

    def test_project_member_asdict_with_none_values(self):
        """Test that asdict excludes None values.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        member = ProjectMember(
            username="john.doe",
            type="account",
            role="editor"
        )

        result = member.asdict()

        assert "name" not in result
        assert result == {
            "username": "john.doe",
            "type": "account",
            "role": "editor"
        }

    def test_project_member_asdict_group_member(self):
        """Test asdict for group member without username.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        member = ProjectMember(
            name="Admins",
            type="group",
            role="owner"
        )

        result = member.asdict()

        assert "username" not in result
        assert result == {
            "name": "Admins",
            "type": "group",
            "role": "owner"
        }

    def test_project_member_asdict_minimal_fields(self):
        """Test asdict with only required/default fields.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        member = ProjectMember()

        result = member.asdict()

        # Only role should be present (has a default)
        assert result == {"role": "viewer"}

    def test_project_member_immutability(self):
        """Test that ProjectMember is immutable (frozen=True).

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        member = ProjectMember(username="john.doe", type="account")

        with pytest.raises((AttributeError, TypeError)):  # Frozen dataclass error
            member.username = "jane.smith"

    def test_project_member_slots(self):
        """Test that ProjectMember uses slots for memory efficiency.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        member = ProjectMember(username="john.doe")

        # Should not be able to add arbitrary attributes with slots and frozen
        with pytest.raises((AttributeError, TypeError)):
            member.arbitrary_attr = "value"

    def test_project_member_keyword_only(self):
        """Test that ProjectMember requires keyword arguments.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Should raise TypeError if we try to pass positional args
        with pytest.raises(TypeError):
            ProjectMember("john.doe", "account", "editor")

    def test_project_member_equality(self):
        """Test equality comparison between ProjectMember instances.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        member1 = ProjectMember(username="john.doe", type="account", role="editor")
        member2 = ProjectMember(username="john.doe", type="account", role="editor")
        member3 = ProjectMember(username="jane.smith", type="account", role="editor")

        assert member1 == member2
        assert member1 != member3

    def test_project_member_hash(self):
        """Test that ProjectMember instances are hashable (frozen).

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        member1 = ProjectMember(username="john.doe", type="account", role="editor")
        member2 = ProjectMember(username="john.doe", type="account", role="editor")

        # Should be able to use in a set
        member_set = {member1, member2}
        # Since they're equal and hashable, should only have one item
        assert len(member_set) == 1

    def test_project_member_repr(self):
        """Test string representation of ProjectMember.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        member = ProjectMember(username="john.doe", type="account", role="editor")

        repr_str = repr(member)

        assert "ProjectMember" in repr_str
        assert "username='john.doe'" in repr_str
        assert "type='account'" in repr_str
        assert "role='editor'" in repr_str

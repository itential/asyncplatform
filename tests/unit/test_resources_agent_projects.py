# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.resources.agent_projects module."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest

from asyncplatform import exceptions
from asyncplatform.models.projects import ProjectMember
from asyncplatform.resources.agent_projects import Resource


class TestResourceInit:
    """Test suite for Resource initialization."""

    def test_resource_initialization(self):
        """Test Resource initializes with client and sets cache attributes to None."""
        mock_client = MagicMock()
        resource = Resource(mock_client)

        assert resource.client is mock_client
        assert resource._groups_cache is None
        assert resource._accounts_cache is None

    def test_resource_agent_projects_property(self):
        """Test agent_projects property returns the client's agent_projects service."""
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()
        mock_client.agent_projects = mock_agent_projects

        resource = Resource(mock_client)
        assert resource.agent_projects is mock_agent_projects

    def test_resource_authorization_property(self):
        """Test authorization property returns the client's authorization service."""
        mock_client = MagicMock()
        mock_auth = MagicMock()
        mock_client.authorization = mock_auth

        resource = Resource(mock_client)
        assert resource.authorization is mock_auth


class TestGetGroups:
    """Test suite for _get_groups method."""

    @pytest.mark.asyncio
    async def test_get_groups_first_call(self):
        """Test that _get_groups fetches and caches groups on first call.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_auth = MagicMock()
        mock_auth.get_groups = AsyncMock(
            return_value=[
                {"_id": "1", "name": "Admins"},
                {"_id": "2", "name": "Operators"},
            ]
        )
        mock_client.authorization = mock_auth

        resource = Resource(mock_client)
        result = await resource.get_groups()

        assert result == {
            "Admins": {"_id": "1", "name": "Admins"},
            "Operators": {"_id": "2", "name": "Operators"},
        }
        assert resource._groups_cache == result
        mock_auth.get_groups.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_groups_cached_call(self):
        """Test that _get_groups returns cached data on subsequent calls.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_auth = MagicMock()
        mock_auth.get_groups = AsyncMock(
            return_value=[
                {"_id": "1", "name": "Admins"},
            ]
        )
        mock_client.authorization = mock_auth

        resource = Resource(mock_client)

        # First call
        result1 = await resource.get_groups()
        # Second call
        result2 = await resource.get_groups()

        assert result1 == result2
        # Should only be called once due to caching
        mock_auth.get_groups.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_groups_empty_list(self):
        """Test that _get_groups handles empty groups list.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_auth = MagicMock()
        mock_auth.get_groups = AsyncMock(return_value=[])
        mock_client.authorization = mock_auth

        resource = Resource(mock_client)
        result = await resource.get_groups()

        assert result == {}


class TestGetAccounts:
    """Test suite for _get_accounts method."""

    @pytest.mark.asyncio
    async def test_get_accounts_first_call(self):
        """Test that _get_accounts fetches and caches accounts on first call.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_auth = MagicMock()
        mock_auth.get_accounts = AsyncMock(
            return_value=[
                {"_id": "1", "username": "john.doe"},
                {"_id": "2", "username": "jane.smith"},
            ]
        )
        mock_client.authorization = mock_auth

        resource = Resource(mock_client)
        result = await resource.get_accounts()

        assert result == {
            "john.doe": {"_id": "1", "username": "john.doe"},
            "jane.smith": {"_id": "2", "username": "jane.smith"},
        }
        assert resource._accounts_cache == result
        mock_auth.get_accounts.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_accounts_cached_call(self):
        """Test that _get_accounts returns cached data on subsequent calls.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_auth = MagicMock()
        mock_auth.get_accounts = AsyncMock(
            return_value=[
                {"_id": "1", "username": "john.doe"},
            ]
        )
        mock_client.authorization = mock_auth

        resource = Resource(mock_client)

        # First call
        result1 = await resource.get_accounts()
        # Second call
        result2 = await resource.get_accounts()

        assert result1 == result2
        # Should only be called once due to caching
        mock_auth.get_accounts.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_accounts_empty_list(self):
        """Test that _get_accounts handles empty accounts list.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_auth = MagicMock()
        mock_auth.get_accounts = AsyncMock(return_value=[])
        mock_client.authorization = mock_auth

        resource = Resource(mock_client)
        result = await resource.get_accounts()

        assert result == {}


class TestResolveMemberReference:
    """Test suite for _resolve_member_reference method."""

    @pytest.mark.asyncio
    async def test_resolve_group_member(self):
        """Test resolving a group member reference.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        resource = Resource(mock_client)

        member = ProjectMember(name="Admins", type="group", role="owner")
        all_groups = {"Admins": {"_id": "group1", "name": "Admins"}}
        all_accounts = {}

        ref_id, display_name = await resource._resolve_member_reference(
            member, all_groups, all_accounts
        )

        assert ref_id == "group1"
        assert display_name == "Admins"

    @pytest.mark.asyncio
    async def test_resolve_account_member(self):
        """Test resolving an account member reference.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        resource = Resource(mock_client)

        member = ProjectMember(username="john.doe", type="account", role="editor")
        all_groups = {}
        all_accounts = {"john.doe": {"_id": "user1", "username": "john.doe"}}

        ref_id, display_name = await resource._resolve_member_reference(
            member, all_groups, all_accounts
        )

        assert ref_id == "user1"
        assert display_name == "john.doe"

    @pytest.mark.asyncio
    async def test_resolve_invalid_member_type(self):
        """Test that invalid member type raises error.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        resource = Resource(mock_client)

        member = ProjectMember(name="test", type="invalid", role="viewer")
        all_groups = {}
        all_accounts = {}

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource._resolve_member_reference(member, all_groups, all_accounts)

        assert "Invalid member type `invalid`" in str(exc_info.value)
        assert "must be 'group' or 'account'" in str(exc_info.value)


class TestSetMembers:
    """Test suite for set_members method."""

    @pytest.mark.asyncio
    async def test_set_members_add_to_existing(self):
        """Test adding members to existing project members.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()

        mock_agent_projects.find_agent_projects = AsyncMock(
            return_value=[
                {
                    "_id": "proj1",
                    "name": "Test Project",
                    "members": [{"reference": "existing1", "type": "group", "role": "editor", "name": "ExistingGroup"}],
                }
            ]
        )
        mock_patch_response = Mock()
        mock_patch_response.json.return_value = {"data": {"_id": "proj1"}}
        mock_agent_projects.patch_agent_project = AsyncMock(return_value=mock_patch_response)

        mock_client.agent_projects = mock_agent_projects

        resource = Resource(mock_client)
        resource.get_groups = AsyncMock(
            return_value={
                "NewGroup": {"_id": "group2", "name": "NewGroup"},
                "ExistingGroup": {"_id": "existing1", "name": "ExistingGroup"},
            }
        )
        resource.get_accounts = AsyncMock(return_value={})

        members = [ProjectMember(name="NewGroup", type="group", role="editor")]
        print(members)
        result = await resource.set_members(
            "Test Project", members, preserve_existing_members=True
        )

        assert result["_id"] == "proj1"
        mock_agent_projects.find_agent_projects.assert_called_once_with(name="Test Project")
        mock_agent_projects.patch_agent_project.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_members_replace_existing(self):
        """Test replacing all existing members with new ones.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()

        mock_agent_projects.find_agent_projects = AsyncMock(
            return_value=[
                {
                    "_id": "proj1",
                    "name": "Test Project",
                    "members": [
                        {"reference": "old1", "type": "group"},
                        {"reference": "old2", "type": "account"},
                    ],
                }
            ]
        )
        mock_patch_response = Mock()
        mock_patch_response.json.return_value = {"data": {"_id": "proj1"}}
        mock_agent_projects.patch_agent_project = AsyncMock(return_value=mock_patch_response)

        mock_client.agent_projects = mock_agent_projects

        resource = Resource(mock_client)
        resource.get_groups = AsyncMock(
            return_value={"NewGroup": {"_id": "newgroup", "name": "NewGroup"}}
        )
        resource.get_accounts = AsyncMock(return_value={})

        members = [ProjectMember(name="NewGroup", type="group", role="owner")]

        result = await resource.set_members(
            "Test Project", members, preserve_existing_members=False
        )

        assert result["_id"] == "proj1"
        # Verify members were cleared before adding new ones
        call_args = mock_agent_projects.patch_agent_project.call_args
        members_list = call_args[0][1]["members"]
        # Should only have the new member, not old ones
        assert len(members_list) == 1

    @pytest.mark.asyncio
    async def test_set_members_project_not_found(self):
        """Test that error is raised when project is not found.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()

        mock_agent_projects.find_agent_projects = AsyncMock(return_value=[])
        mock_client.agent_projects = mock_agent_projects

        resource = Resource(mock_client)
        members = [ProjectMember(name="Group", type="group", role="owner")]

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.set_members("NonExistent", members)

        assert "Could not uniquely identify project NonExistent" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_set_members_multiple_matches(self):
        """Test that error is raised when multiple projects match name.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()

        mock_agent_projects.find_agent_projects = AsyncMock(
            return_value=[
                {"_id": "proj1", "name": "Duplicate"},
                {"_id": "proj2", "name": "Duplicate"},
            ]
        )
        mock_client.agent_projects = mock_agent_projects

        resource = Resource(mock_client)
        members = [ProjectMember(name="Group", type="group", role="owner")]

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.set_members("Duplicate", members)

        assert "Could not uniquely identify project Duplicate" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_set_members_with_nonexistent_member(self):
        """Test that error is raised when member does not exist.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()

        mock_agent_projects.find_agent_projects = AsyncMock(
            return_value=[{"_id": "proj1", "name": "Test Project", "members": []}]
        )

        mock_client.agent_projects = mock_agent_projects

        resource = Resource(mock_client)
        resource.get_groups = AsyncMock(return_value={})
        resource.get_accounts = AsyncMock(return_value={})

        members = [ProjectMember(name="NonExistent", type="group", role="owner")]

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.set_members("Test Project", members)

        assert "does not exist" in str(exc_info.value)



class TestImporter:
    """Test suite for importer method."""

    @pytest.mark.asyncio
    async def test_importer_without_members(self):
        """Test importer imports project and returns result when no members specified."""
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()
        mock_agent_projects.find_agent_projects = AsyncMock(return_value=[])
        mock_agent_projects.import_agent_project = AsyncMock(
            return_value={"_id": "proj1", "name": "Test Project"}
        )
        mock_client.agent_projects = mock_agent_projects

        resource = Resource(mock_client)
        project = {"name": "Test Project", "description": "Test"}

        result = await resource.importer(project)

        assert result == {"_id": "proj1", "name": "Test Project"}
        mock_agent_projects.find_agent_projects.assert_called_once_with(name="Test Project")
        mock_agent_projects.import_agent_project.assert_called_once_with(project)

    @pytest.mark.asyncio
    async def test_importer_raises_when_project_exists_and_overwrite_false(self):
        """Test importer raises AsyncPlatformError when project exists and overwrite=False."""
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()
        mock_agent_projects.find_agent_projects = AsyncMock(
            return_value=[{"_id": "existing", "name": "Test Project"}]
        )
        mock_client.agent_projects = mock_agent_projects

        resource = Resource(mock_client)
        project = {"name": "Test Project", "description": "Test"}

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.importer(project)

        assert "Project `Test Project` already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_importer_with_overwrite_true_deletes_existing_project(self):
        """Test importer deletes existing project before importing when overwrite=True."""
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()
        mock_agent_projects.find_agent_projects = AsyncMock(
            return_value=[{"_id": "existing", "name": "Test Project"}]
        )
        mock_agent_projects.delete_agent_project = AsyncMock(return_value=None)
        mock_agent_projects.import_agent_project = AsyncMock(return_value=None)
        mock_client.agent_projects = mock_agent_projects

        resource = Resource(mock_client)
        project = {"name": "Test Project", "description": "Test2"}

        await resource.importer(project, overwrite=True)

        mock_agent_projects.delete_agent_project.assert_called_once()

    @pytest.mark.asyncio
    async def test_importer_with_overwrite_true_no_existing_project(self):
        """Test importer skips delete and imports directly when overwrite=True and project absent."""
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()
        mock_agent_projects.find_agent_projects = AsyncMock(
            return_value=[]
        )
        mock_agent_projects.delete_agent_project = AsyncMock(return_value=None)
        mock_agent_projects.import_agent_project = AsyncMock(return_value=None)
        mock_client.agent_projects = mock_agent_projects

        resource = Resource(mock_client)
        project = {"name": "Test Project", "description": "Test2"}

        await resource.importer(project, overwrite=True)

        mock_agent_projects.delete_agent_project.assert_not_called()

    @pytest.mark.asyncio
    async def test_importer_with_group_member(self):
        """Test importer calls _update_project_members when a group member is provided."""
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()
        resource = Resource(mock_client)
        project = {"_id": "1", "name": "Test Project", "description": "Test2"}
        members = [ProjectMember(name="Admins", type="group", role="editor")]

        mock_agent_projects.find_agent_projects = AsyncMock(
            return_value=[]
        )
        mock_agent_projects.delete_agent_project = AsyncMock(return_value=None)
        mock_agent_projects.import_agent_project = AsyncMock(return_value=project)
        mock_agent_projects.patch_agent_project = AsyncMock(return_value=members)

        resource.get_groups = AsyncMock(
            return_value={"Admins": {"_id": "group1", "name": "Admins"}}
        )
        resource.get_accounts = AsyncMock(return_value={})
        resource._update_project_members = AsyncMock()
        mock_client.agent_projects = mock_agent_projects

        await resource.importer(project, members=members, overwrite=True)

        resource._update_project_members.assert_called_once()

    @pytest.mark.asyncio
    async def test_importer_with_account_member(self):
        """Test importer calls _update_project_members when an account member is provided."""
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()
        resource = Resource(mock_client)
        project = {"_id": "1", "name": "Test Project", "description": "Test2"}
        members = [ProjectMember(name="admin", type="account", role="editor")]

        mock_agent_projects.find_agent_projects = AsyncMock(
            return_value=[]
        )
        mock_agent_projects.delete_agent_project = AsyncMock(return_value=None)
        mock_agent_projects.import_agent_project = AsyncMock(return_value=project)
        mock_agent_projects.patch_agent_project = AsyncMock(return_value=members)

        resource.get_groups = AsyncMock(return_value=None)
        resource.get_accounts = AsyncMock(
            return_value={"admin": {"_id": "account1", "name": "admin"}}
        )
        resource._update_project_members = AsyncMock()
        mock_client.agent_projects = mock_agent_projects

        await resource.importer(project, members=members, overwrite=True)

        resource._update_project_members.assert_called_once()

    @pytest.mark.asyncio
    async def test_importer_with_multiple_members(self):
        """Test importer passes all members to _update_project_members."""
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()
        resource = Resource(mock_client)
        project = {"_id": "1", "name": "Test Project", "description": "Test2"}
        members = [
            ProjectMember(username="admin", type="account", role="editor"),
            ProjectMember(username="admin2", type="account", role="editor"),
            ProjectMember(username="admin3", type="account", role="editor"),
        ]

        mock_agent_projects.find_agent_projects = AsyncMock(return_value=[])
        mock_agent_projects.import_agent_project = AsyncMock(return_value=project)

        resource._update_project_members = AsyncMock()
        mock_client.agent_projects = mock_agent_projects

        await resource.importer(project, members=members, overwrite=True)

        resource._update_project_members.assert_called_once_with(project, members)

    @pytest.mark.asyncio
    async def test_importer_does_not_mutate_input_bundle(self):
        """Test importer operates on a deep copy so the caller's bundle is unchanged."""
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()
        mock_agent_projects.find_agent_projects = AsyncMock(return_value=[])
        mock_agent_projects.import_agent_project = AsyncMock(return_value={"_id": "proj1"})
        mock_client.agent_projects = mock_agent_projects

        resource = Resource(mock_client)
        bundle = {"name": "Test Project", "description": "Original", "agents": []}
        original = bundle.copy()

        await resource.importer(bundle)

        assert bundle == original

    @pytest.mark.asyncio
    async def test_importer_skips_member_update_when_members_is_none(self):
        """Test importer does not call _update_project_members when members=None."""
        mock_client = MagicMock()
        mock_agent_projects = MagicMock()
        resource = Resource(mock_client)
        project = {"_id": "1", "name": "Test Project", "description": "Test2"}
        members = []

        mock_agent_projects.find_agent_projects = AsyncMock(return_value=[])
        mock_agent_projects.import_agent_project = AsyncMock(return_value=project)

        resource._update_project_members = AsyncMock()
        mock_client.agent_projects = mock_agent_projects

        await resource.importer(project, members=members, overwrite=True)

        resource._update_project_members.assert_not_called()

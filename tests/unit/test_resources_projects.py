# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.resources.projects module."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from asyncplatform import exceptions
from asyncplatform.models.projects import ProjectMember
from asyncplatform.resources.projects import Resource


class TestResourceInit:
    """Test suite for Resource initialization."""

    def test_resource_initialization(self):
        """Test that Resource initializes correctly with a client.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        resource = Resource(mock_client)

        assert resource.client is mock_client
        assert resource._groups_cache is None
        assert resource._accounts_cache is None

    def test_resource_studio_property(self):
        """Test that studio property returns client's automation_studio.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()
        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        assert resource.studio is mock_studio

    def test_resource_authorization_property(self):
        """Test that authorization property returns client's authorization service.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
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


class TestImporter:
    """Test suite for importer method."""

    @pytest.mark.asyncio
    async def test_importer_without_members(self):
        """Test importing a project without members.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()
        mock_studio.find_projects = AsyncMock(return_value=[])
        mock_studio.import_project = AsyncMock(
            return_value={"_id": "proj1", "name": "Test Project"}
        )
        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        project = {"name": "Test Project", "description": "Test"}

        result = await resource.importer(project)

        assert result == {"_id": "proj1", "name": "Test Project"}
        mock_studio.find_projects.assert_called_once_with(name="Test Project")
        mock_studio.import_project.assert_called_once_with(project)

    @pytest.mark.asyncio
    async def test_importer_project_already_exists(self):
        """Test that importer raises ValueError if project exists.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()
        mock_studio.find_projects = AsyncMock(
            return_value=[{"_id": "existing", "name": "Test Project"}]
        )
        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        project = {"name": "Test Project", "description": "Test"}

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.importer(project)

        assert "Project `Test Project` already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_importer_with_group_member(self):
        """Test importing a project with a group member.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(return_value=[])
        mock_studio.import_project = AsyncMock(
            return_value={"_id": "proj1", "name": "Test Project", "members": []}
        )
        mock_studio.patch_project = AsyncMock(return_value={"_id": "proj1"})

        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        # Mock the get_groups and get_accounts methods directly on the resource
        resource.get_groups = AsyncMock(
            return_value={"Admins": {"_id": "group1", "name": "Admins"}}
        )
        resource.get_accounts = AsyncMock(return_value={})

        project = {"name": "Test Project", "description": "Test"}
        members = [ProjectMember(name="Admins", type="group", role="owner")]

        await resource.importer(project, members=members)

        mock_studio.patch_project.assert_called_once()
        call_args = mock_studio.patch_project.call_args
        assert call_args[0][0] == "proj1"
        assert "members" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_importer_with_account_member(self):
        """Test importing a project with an account member.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(return_value=[])
        mock_studio.import_project = AsyncMock(
            return_value={"_id": "proj1", "name": "Test Project", "members": []}
        )
        mock_studio.patch_project = AsyncMock(return_value={"_id": "proj1"})

        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        # Mock the get_groups and get_accounts methods directly on the resource
        resource.get_groups = AsyncMock(return_value={})
        resource.get_accounts = AsyncMock(
            return_value={"john.doe": {"_id": "user1", "username": "john.doe"}}
        )

        project = {"name": "Test Project", "description": "Test"}
        members = [ProjectMember(username="john.doe", type="account", role="editor")]

        await resource.importer(project, members=members)

        mock_studio.patch_project.assert_called_once()
        call_args = mock_studio.patch_project.call_args
        assert call_args[0][0] == "proj1"
        assert "members" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_importer_with_nonexistent_group(self):
        """Test that importer raises error for nonexistent group.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(return_value=[])
        mock_studio.import_project = AsyncMock(
            return_value={"_id": "proj1", "name": "Test Project", "members": []}
        )

        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        # Mock the get_groups and get_accounts methods directly on the resource
        resource.get_groups = AsyncMock(
            return_value={"Admins": {"_id": "group1", "name": "Admins"}}
        )
        resource.get_accounts = AsyncMock(return_value={})

        project = {"name": "Test Project", "description": "Test"}
        members = [ProjectMember(name="NonExistent", type="group", role="owner")]

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.importer(project, members=members)

        assert "does not exist" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_importer_with_nonexistent_account(self):
        """Test that importer raises error for nonexistent account.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(return_value=[])
        mock_studio.import_project = AsyncMock(
            return_value={"_id": "proj1", "name": "Test Project", "members": []}
        )

        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        # Mock the get_groups and get_accounts methods directly on the resource
        resource.get_groups = AsyncMock(return_value={})
        resource.get_accounts = AsyncMock(
            return_value={"jane.doe": {"_id": "user1", "username": "jane.doe"}}
        )

        project = {"name": "Test Project", "description": "Test"}
        members = [ProjectMember(username="nonexistent", type="account", role="editor")]

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.importer(project, members=members)

        assert "does not exist" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_importer_member_already_exists(self):
        """Test that importer skips member if already in project.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(return_value=[])
        mock_studio.import_project = AsyncMock(
            return_value={
                "_id": "proj1",
                "name": "Test Project",
                "members": [{"reference": "group1", "type": "group", "role": "owner"}],
            }
        )
        mock_studio.patch_project = AsyncMock(return_value={"_id": "proj1"})

        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        # Mock the get_groups and get_accounts methods directly on the resource
        resource.get_groups = AsyncMock(
            return_value={"Admins": {"_id": "group1", "name": "Admins"}}
        )
        resource.get_accounts = AsyncMock(return_value={})

        project = {"name": "Test Project", "description": "Test"}
        members = [ProjectMember(name="Admins", type="group", role="owner")]

        await resource.importer(project, members=members)

        # Should not call patch_project since member already exists
        mock_studio.patch_project.assert_not_called()

    @pytest.mark.asyncio
    async def test_importer_with_multiple_members(self):
        """Test importing a project with multiple members.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()
        mock_auth = MagicMock()

        mock_studio.find_projects = AsyncMock(return_value=[])
        mock_studio.import_project = AsyncMock(
            return_value={"_id": "proj1", "name": "Test Project", "members": []}
        )
        mock_studio.patch_project = AsyncMock(return_value={"_id": "proj1"})

        mock_auth.get_groups = AsyncMock(
            return_value=[{"_id": "group1", "name": "Admins"}]
        )
        mock_auth.get_accounts = AsyncMock(
            return_value=[{"_id": "user1", "username": "john.doe"}]
        )

        mock_client.automation_studio = mock_studio
        mock_client.authorization = mock_auth

        resource = Resource(mock_client)
        project = {"name": "Test Project", "description": "Test"}
        members = [
            ProjectMember(name="Admins", type="group", role="owner"),
            ProjectMember(username="john.doe", type="account", role="editor"),
        ]

        await resource.importer(project, members=members)

        mock_studio.patch_project.assert_called_once()
        call_args = mock_studio.patch_project.call_args
        members_list = call_args[0][1]["members"]
        assert len(members_list) == 2

    @pytest.mark.asyncio
    async def test_importer_preserve_existing_members_true(self):
        """Test importing project with preserve_existing_members=True.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(return_value=[])
        mock_studio.import_project = AsyncMock(
            return_value={
                "_id": "proj1",
                "name": "Test Project",
                "members": [
                    {"reference": "existing1", "type": "group", "role": "viewer"}
                ],
            }
        )
        mock_studio.patch_project = AsyncMock(return_value={"_id": "proj1"})

        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        resource.get_groups = AsyncMock(
            return_value={"NewGroup": {"_id": "group2", "name": "NewGroup"}}
        )
        resource.get_accounts = AsyncMock(return_value={})

        project = {"name": "Test Project", "description": "Test"}
        members = [ProjectMember(name="NewGroup", type="group", role="owner")]

        await resource.importer(
            project, members=members, preserve_existing_members=True
        )

        # Verify existing member was preserved
        mock_studio.patch_project.assert_called_once()
        call_args = mock_studio.patch_project.call_args
        members_list = call_args[0][1]["members"]
        # Should have both existing and new member
        assert len(members_list) == 2
        assert any(m["reference"] == "existing1" for m in members_list)
        assert any(m["reference"] == "group2" for m in members_list)

    @pytest.mark.asyncio
    async def test_importer_preserve_existing_members_false(self):
        """Test importing project with preserve_existing_members=False.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(return_value=[])
        mock_studio.import_project = AsyncMock(
            return_value={
                "_id": "proj1",
                "name": "Test Project",
                "members": [
                    {"reference": "existing1", "type": "group", "role": "viewer"},
                    {"reference": "existing2", "type": "account", "role": "editor"},
                ],
            }
        )
        mock_studio.patch_project = AsyncMock(return_value={"_id": "proj1"})

        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        resource.get_groups = AsyncMock(
            return_value={"NewGroup": {"_id": "group2", "name": "NewGroup"}}
        )
        resource.get_accounts = AsyncMock(return_value={})

        project = {"name": "Test Project", "description": "Test"}
        members = [ProjectMember(name="NewGroup", type="group", role="owner")]

        await resource.importer(
            project, members=members, preserve_existing_members=False
        )

        # Verify existing members were cleared
        mock_studio.patch_project.assert_called_once()
        call_args = mock_studio.patch_project.call_args
        members_list = call_args[0][1]["members"]
        # Should only have the new member, not existing ones
        assert len(members_list) == 1
        assert members_list[0]["reference"] == "group2"
        assert not any(m["reference"] == "existing1" for m in members_list)
        assert not any(m["reference"] == "existing2" for m in members_list)

    @pytest.mark.asyncio
    async def test_importer_preserve_existing_members_false_no_new_members(self):
        """Test importing with preserve_existing_members=False and no new members.

        When members=None, no member updates occur regardless of the
        preserve_existing_members flag, so existing members remain unchanged.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(return_value=[])
        mock_studio.import_project = AsyncMock(
            return_value={
                "_id": "proj1",
                "name": "Test Project",
                "members": [
                    {"reference": "existing1", "type": "group", "role": "viewer"}
                ],
            }
        )

        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        project = {"name": "Test Project", "description": "Test"}

        result = await resource.importer(
            project, members=None, preserve_existing_members=False
        )

        # When members=None, no member processing occurs, so existing members remain
        assert result["_id"] == "proj1"
        assert len(result["members"]) == 1
        assert result["members"][0]["reference"] == "existing1"
        # patch_project should not be called since members=None
        mock_studio.patch_project.assert_not_called()

    @pytest.mark.asyncio
    async def test_importer_with_overwrite_true_deletes_existing(self):
        """Test that overwrite=True deletes existing project before importing.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()

        # Mock finding existing project
        mock_studio.find_projects = AsyncMock(
            return_value=[{"_id": "existing_proj", "name": "Test Project"}]
        )
        # Mock deleting existing project
        mock_studio.delete_project = AsyncMock(return_value={"message": "Deleted"})
        # Mock importing new project
        mock_studio.import_project = AsyncMock(
            return_value={"_id": "new_proj", "name": "Test Project"}
        )

        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        project = {"name": "Test Project", "description": "Updated project"}

        result = await resource.importer(project, overwrite=True)

        # Verify existing project was found
        mock_studio.find_projects.assert_called_once_with(name="Test Project")
        # Verify existing project was deleted
        mock_studio.delete_project.assert_called_once_with("existing_proj")
        # Verify new project was imported
        mock_studio.import_project.assert_called_once()
        assert result["_id"] == "new_proj"
        assert result["name"] == "Test Project"

    @pytest.mark.asyncio
    async def test_importer_with_overwrite_true_no_existing_project(self):
        """Test that overwrite=True works when no existing project exists.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()

        # No existing project found
        mock_studio.find_projects = AsyncMock(return_value=[])
        mock_studio.delete_project = AsyncMock()
        mock_studio.import_project = AsyncMock(
            return_value={"_id": "proj1", "name": "Test Project"}
        )

        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        project = {"name": "Test Project", "description": "New project"}

        result = await resource.importer(project, overwrite=True)

        # Verify search was performed
        mock_studio.find_projects.assert_called_once_with(name="Test Project")
        # Verify no deletion occurred since project didn't exist
        mock_studio.delete_project.assert_not_called()
        # Verify project was imported
        mock_studio.import_project.assert_called_once()
        assert result["_id"] == "proj1"

    @pytest.mark.asyncio
    async def test_importer_with_overwrite_false_raises_on_existing(self):
        """Test that overwrite=False raises error when project exists.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(
            return_value=[{"_id": "existing", "name": "Test Project"}]
        )
        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        project = {"name": "Test Project", "description": "Test"}

        # Test with explicit overwrite=False
        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.importer(project, overwrite=False)

        assert "Project `Test Project` already exists" in str(exc_info.value)
        # Verify delete was never called
        mock_studio.delete_project.assert_not_called()

    @pytest.mark.asyncio
    async def test_importer_overwrite_default_false(self):
        """Test that overwrite parameter defaults to False.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(
            return_value=[{"_id": "existing", "name": "Test Project"}]
        )
        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        project = {"name": "Test Project", "description": "Test"}

        # Test without specifying overwrite (should default to False)
        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.importer(project)

        assert "Project `Test Project` already exists" in str(exc_info.value)


class TestDelete:
    """Test suite for delete method."""

    @pytest.mark.asyncio
    async def test_delete_existing_project(self):
        """Test deleting an existing project.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()
        mock_studio.find_projects = AsyncMock(
            return_value=[{"_id": "proj1", "name": "Test Project"}]
        )
        mock_studio.delete_project = AsyncMock(
            return_value={"message": "Project deleted", "data": {}, "metadata": {}}
        )
        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        result = await resource.delete("Test Project")

        assert result["message"] == "Project deleted"
        mock_studio.find_projects.assert_called_once_with(name="Test Project")
        mock_studio.delete_project.assert_called_once_with("proj1")

    @pytest.mark.asyncio
    async def test_delete_nonexistent_project(self):
        """Test deleting a project that doesn't exist.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()
        mock_studio.find_projects = AsyncMock(return_value=[])
        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        result = await resource.delete("NonExistent")

        assert result == {}
        mock_studio.find_projects.assert_called_once_with(name="NonExistent")
        mock_studio.delete_project.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_first_match_when_multiple(self):
        """Test that delete removes the first matching project.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()
        mock_studio.find_projects = AsyncMock(
            return_value=[
                {"_id": "proj1", "name": "Test Project"},
                {"_id": "proj2", "name": "Test Project"},
            ]
        )
        mock_studio.delete_project = AsyncMock(return_value={"message": "Deleted"})
        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        await resource.delete("Test Project")

        # Should delete the first match
        mock_studio.delete_project.assert_called_once_with("proj1")


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
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(
            return_value=[
                {
                    "_id": "proj1",
                    "name": "Test Project",
                    "members": [{"reference": "existing1", "type": "group"}],
                }
            ]
        )
        mock_studio.patch_project = AsyncMock(return_value={"_id": "proj1"})

        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        resource.get_groups = AsyncMock(
            return_value={"NewGroup": {"_id": "group2", "name": "NewGroup"}}
        )
        resource.get_accounts = AsyncMock(return_value={})

        members = [ProjectMember(name="NewGroup", type="group", role="editor")]

        result = await resource.set_members(
            "Test Project", members, preserve_existing_members=True
        )

        assert result["_id"] == "proj1"
        mock_studio.find_projects.assert_called_once_with(name="Test Project")
        mock_studio.patch_project.assert_called_once()

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
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(
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
        mock_studio.patch_project = AsyncMock(return_value={"_id": "proj1"})

        mock_client.automation_studio = mock_studio

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
        call_args = mock_studio.patch_project.call_args
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
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(return_value=[])
        mock_client.automation_studio = mock_studio

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
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(
            return_value=[
                {"_id": "proj1", "name": "Duplicate"},
                {"_id": "proj2", "name": "Duplicate"},
            ]
        )
        mock_client.automation_studio = mock_studio

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
        mock_studio = MagicMock()

        mock_studio.find_projects = AsyncMock(
            return_value=[{"_id": "proj1", "name": "Test Project", "members": []}]
        )

        mock_client.automation_studio = mock_studio

        resource = Resource(mock_client)
        resource.get_groups = AsyncMock(return_value={})
        resource.get_accounts = AsyncMock(return_value={})

        members = [ProjectMember(name="NonExistent", type="group", role="owner")]

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.set_members("Test Project", members)

        assert "does not exist" in str(exc_info.value)

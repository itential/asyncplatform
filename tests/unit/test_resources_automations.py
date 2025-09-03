# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.resources.automations module."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from asyncplatform import exceptions
from asyncplatform.resources.automations import Resource


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

    def test_resource_name_attribute(self):
        """Test that Resource has correct name attribute.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert hasattr(Resource, "name")
        assert Resource.name == "automations"

    def test_resource_operations_manager_property(self):
        """Test that operations_manager property returns client's operations_manager service.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)
        assert resource.operations_manager is mock_ops_mgr

    def test_resource_studio_property(self):
        """Test that studio property returns client's automation_studio service.

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


class TestCheckIfAutomationExists:
    """Test suite for _check_if_automation_exists method."""

    @pytest.mark.asyncio
    async def test_check_if_automation_exists_returns_true(self):
        """Test that _check_if_automation_exists returns True when automation exists.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_ops_mgr.find_automations = AsyncMock(return_value=[
            {"_id": "1", "name": "TestAutomation"}
        ])
        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)
        result = await resource._check_if_automation_exists("TestAutomation")

        assert result is True
        mock_ops_mgr.find_automations.assert_called_once_with(name="TestAutomation")

    @pytest.mark.asyncio
    async def test_check_if_automation_exists_returns_false(self):
        """Test that _check_if_automation_exists returns False when automation doesn't exist.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_ops_mgr.find_automations = AsyncMock(return_value=[])
        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)
        result = await resource._check_if_automation_exists("NonExistent")

        assert result is False


class TestValidateGbac:
    """Test suite for _validate_gbac method."""

    @pytest.mark.asyncio
    async def test_validate_gbac_all_groups_exist(self):
        """Test _validate_gbac when all groups exist.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        resource = Resource(mock_client)

        gbac = {
            "read": [{"name": "Readers"}, {"name": "Viewers"}],
            "write": [{"name": "Writers"}]
        }
        all_groups = {
            "Readers": {"_id": "1", "name": "Readers"},
            "Viewers": {"_id": "2", "name": "Viewers"},
            "Writers": {"_id": "3", "name": "Writers"}
        }

        missing = await resource._validate_gbac(gbac, all_groups)

        assert len(missing) == 0

    @pytest.mark.asyncio
    async def test_validate_gbac_some_groups_missing(self):
        """Test _validate_gbac when some groups are missing.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        resource = Resource(mock_client)

        gbac = {
            "read": [{"name": "Readers"}, {"name": "MissingGroup"}],
            "write": [{"name": "Writers"}]
        }
        all_groups = {
            "Readers": {"_id": "1", "name": "Readers"},
            "Writers": {"_id": "3", "name": "Writers"}
        }

        missing = await resource._validate_gbac(gbac, all_groups)

        assert len(missing) == 1
        assert missing[0]["name"] == "MissingGroup"

    @pytest.mark.asyncio
    async def test_validate_gbac_empty_groups(self):
        """Test _validate_gbac with empty GBAC groups.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        resource = Resource(mock_client)

        gbac = {
            "read": [],
            "write": []
        }
        all_groups = {}

        missing = await resource._validate_gbac(gbac, all_groups)

        assert len(missing) == 0


class TestGetAutomationIdForName:
    """Test suite for get_automation_id_for_name method."""

    @pytest.mark.asyncio
    async def test_get_automation_id_for_name_found(self):
        """Test get_automation_id_for_name returns ID when automation is found.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_ops_mgr.find_automations = AsyncMock(return_value=[
            {"_id": "auto123", "name": "TargetAutomation"}
        ])
        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)
        result = await resource.get_automation_by_name("TargetAutomation")

        assert result == {"_id": "auto123", "name": "TargetAutomation"}

    @pytest.mark.asyncio
    async def test_get_automation_id_for_name_not_found(self):
        """Test get_automation_by_name returns None when automation not found.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_ops_mgr.find_automations = AsyncMock(return_value=[])
        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)
        result = await resource.get_automation_by_name("NonExistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_automation_id_for_name_exact_match(self):
        """Test get_automation_by_name returns exact name match only.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_ops_mgr.find_automations = AsyncMock(return_value=[
            {"_id": "auto1", "name": "Target"},
            {"_id": "auto2", "name": "TargetAutomation"},
            {"_id": "auto3", "name": "TargetOther"}
        ])
        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)
        result = await resource.get_automation_by_name("TargetAutomation")

        assert result == {"_id": "auto2", "name": "TargetAutomation"}


class TestIsWorkflow:
    """Test suite for _is_workflow method."""

    @pytest.mark.asyncio
    async def test_is_workflow_valid(self):
        """Test _is_workflow doesn't raise error for valid workflow type.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        resource = Resource(mock_client)

        automation = {"componentType": "workflows"}

        # Should not raise any exception
        await resource._is_workflow(automation)

    @pytest.mark.asyncio
    async def test_is_workflow_invalid_type(self):
        """Test _is_workflow raises error for invalid component type.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        resource = Resource(mock_client)

        automation = {"componentType": "jobs"}

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource._is_workflow(automation)

        assert "expected `workflows`" in str(exc_info.value)
        assert "got `jobs`" in str(exc_info.value)


class TestEnsureAutomationIsNew:
    """Test suite for _ensure_automation_is_new method."""

    @pytest.mark.asyncio
    async def test_ensure_automation_is_new_succeeds(self):
        """Test _ensure_automation_is_new succeeds when automation doesn't exist.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_ops_mgr.find_automations = AsyncMock(return_value=[])
        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)

        # Should not raise exception
        await resource._ensure_automation_is_new("NewAutomation")

    @pytest.mark.asyncio
    async def test_ensure_automation_is_new_raises_error(self):
        """Test _ensure_automation_is_new raises error when automation exists.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_ops_mgr.find_automations = AsyncMock(return_value=[
            {"_id": "auto1", "name": "ExistingAutomation"}
        ])
        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource._ensure_automation_is_new("ExistingAutomation")

        assert "already exists" in str(exc_info.value)


class TestImporter:
    """Test suite for importer method."""

    @pytest.mark.asyncio
    async def test_importer_success(self):
        """Test importer successfully imports automation.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_auth = MagicMock()

        # Mock find_automations to return empty (automation doesn't exist)
        mock_ops_mgr.find_automations = AsyncMock(return_value=[])

        # Mock import_automation
        mock_ops_mgr.import_automation = AsyncMock(return_value={
            "_id": "new_auto",
            "name": "TestAutomation"
        })

        # Mock get_groups for GBAC
        mock_auth.get_groups = AsyncMock(return_value=[
            {"_id": "1", "name": "Admins"}
        ])

        mock_client.operations_manager = mock_ops_mgr
        mock_client.authorization = mock_auth

        resource = Resource(mock_client)

        automation = {
            "name": "TestAutomation",
            "componentType": "workflows",
            "gbac": {
                "read": [{"name": "Admins"}],
                "write": [{"name": "Admins"}]
            }
        }

        result = await resource.importer(automation)

        assert result["_id"] == "new_auto"
        assert result["name"] == "TestAutomation"

    @pytest.mark.asyncio
    async def test_importer_validates_component_type(self):
        """Test importer validates component type.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_ops_mgr.find_automations = AsyncMock(return_value=[])
        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)

        automation = {
            "name": "TestAutomation",
            "componentType": "jobs"
        }

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.importer(automation)

        assert "expected `workflows`" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_importer_checks_for_duplicates(self):
        """Test importer checks for duplicate automations.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_ops_mgr.find_automations = AsyncMock(return_value=[
            {"_id": "existing", "name": "TestAutomation"}
        ])
        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)

        automation = {
            "name": "TestAutomation",
            "componentType": "workflows",
            "gbac": {"read": [], "write": []}
        }

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.importer(automation)

        assert "already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_importer_doesnt_mutate_input(self):
        """Test importer doesn't mutate original automation dictionary.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_auth = MagicMock()

        mock_ops_mgr.find_automations = AsyncMock(return_value=[])
        mock_ops_mgr.import_automation = AsyncMock(return_value={
            "_id": "new_auto",
            "name": "TestAutomation"
        })
        mock_auth.get_groups = AsyncMock(return_value=[
            {"_id": "1", "name": "Admins"}
        ])

        mock_client.operations_manager = mock_ops_mgr
        mock_client.authorization = mock_auth

        resource = Resource(mock_client)

        original_automation = {
            "name": "TestAutomation",
            "componentType": "workflows",
            "gbac": {
                "read": [],
                "write": []
            }
        }

        import copy
        original_copy = copy.deepcopy(original_automation)

        await resource.importer(
            original_automation,
            write_groups=["Admins"],
            preserve_write_groups=False
        )

        # Verify original wasn't mutated
        assert original_automation == original_copy

    @pytest.mark.asyncio
    async def test_importer_with_preserve_groups_false(self):
        """Test importer with preserve_groups set to False.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_auth = MagicMock()

        mock_ops_mgr.find_automations = AsyncMock(return_value=[])
        mock_ops_mgr.import_automation = AsyncMock(return_value={
            "_id": "new_auto",
            "name": "TestAutomation"
        })
        mock_auth.get_groups = AsyncMock(return_value=[
            {"_id": "1", "name": "NewGroup"}
        ])

        mock_client.operations_manager = mock_ops_mgr
        mock_client.authorization = mock_auth

        resource = Resource(mock_client)

        automation = {
            "name": "TestAutomation",
            "componentType": "workflows",
            "gbac": {
                "read": [{"name": "OldGroup"}],
                "write": [{"name": "OldGroup"}]
            }
        }

        result = await resource.importer(
            automation,
            write_groups=["NewGroup"],
            preserve_read_groups=False,
            preserve_write_groups=False
        )

        assert result["_id"] == "new_auto"


class TestDelete:
    """Test suite for delete method."""

    @pytest.mark.asyncio
    async def test_delete_success(self):
        """Test delete successfully deletes automation by name.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_ops_mgr.find_automations = AsyncMock(return_value=[
            {"_id": "auto123", "name": "TargetAutomation"}
        ])
        mock_ops_mgr.delete_automation = AsyncMock(return_value={
            "message": "Successfully deleted"
        })
        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)
        result = await resource.delete("TargetAutomation")

        assert result is None
        mock_ops_mgr.delete_automation.assert_called_once_with("auto123")

    @pytest.mark.asyncio
    async def test_delete_not_found(self):
        """Test delete returns None when automation not found.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_ops_mgr.find_automations = AsyncMock(return_value=[])
        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)
        result = await resource.delete("NonExistent")

        assert result is None
        # Should not call delete_automation
        mock_ops_mgr.delete_automation.assert_not_called()


class TestProcessGbac:
    """Test suite for _process_gbac method."""

    @pytest.mark.asyncio
    async def test_process_gbac_validates_missing_groups(self):
        """Test _process_gbac raises error for missing groups.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_auth = MagicMock()
        mock_auth.get_groups = AsyncMock(return_value=[
            {"_id": "1", "name": "ExistingGroup"}
        ])
        mock_client.authorization = mock_auth

        resource = Resource(mock_client)

        gbac = {
            "read": [{"name": "MissingGroup"}],
            "write": []
        }

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource._process_gbac(
                gbac,
                write_groups=None,
                read_groups=None,
                preserve_read_groups=True,
                preserve_write_groups=True
            )

        assert "missing groups" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_process_gbac_success(self):
        """Test _process_gbac successfully processes GBAC configuration.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_auth = MagicMock()
        mock_auth.get_groups = AsyncMock(return_value=[
            {"_id": "1", "name": "Group1"},
            {"_id": "2", "name": "Group2"}
        ])
        mock_client.authorization = mock_auth

        resource = Resource(mock_client)

        gbac = {
            "read": [{"name": "Group1"}],
            "write": []
        }

        # Store original to verify no mutation
        original_write_length = len(gbac["write"])
        original_read = gbac["read"].copy()

        # Should not raise exception and should return new gbac dict
        result = await resource._process_gbac(
            gbac,
            write_groups=["Group2"],
            read_groups=None,
            preserve_read_groups=True,
            preserve_write_groups=True
        )

        # Verify original gbac was not mutated
        assert len(gbac["write"]) == original_write_length
        assert gbac["read"] == original_read

        # Verify returned gbac has Group2 added to write groups
        assert len(result["write"]) == 1
        assert result["write"][0]["name"] == "Group2"

        # Verify returned gbac preserved read groups
        assert len(result["read"]) == 1
        assert result["read"][0]["name"] == "Group1"


class TestSetGbac:
    """Test suite for set_gbac method."""

    @pytest.mark.asyncio
    async def test_set_gbac_updates_automation_gbac(self):
        """Test set_gbac successfully updates automation GBAC configuration.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()

        # Mock get_automation_by_name
        automation = {
            "_id": "auto123",
            "name": "TestAutomation",
            "gbac": {
                "read": [{"_id": "1", "name": "Group1"}],
                "write": []
            }
        }
        mock_ops_mgr.find_automations = AsyncMock(return_value=[automation])
        mock_ops_mgr.get_automation = AsyncMock(return_value=automation)
        mock_ops_mgr.update_automation = AsyncMock(return_value={
            "_id": "auto123",
            "name": "TestAutomation"
        })

        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)
        resource.get_groups = AsyncMock(return_value={
            "Group1": {"_id": "1", "name": "Group1"},
            "Group2": {"_id": "2", "name": "Group2"}
        })

        result = await resource.set_gbac(
            "TestAutomation",
            read_groups=None,
            write_groups=["Group2"],
            preserve_read_groups=True,
            preserve_write_groups=False
        )

        assert result is not None
        mock_ops_mgr.update_automation.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_gbac_preserves_existing_groups(self):
        """Test set_gbac preserves existing groups when preserve flags are True.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()

        automation = {
            "_id": "auto123",
            "name": "TestAutomation",
            "gbac": {
                "read": [{"_id": "1", "name": "Group1"}],
                "write": [{"_id": "2", "name": "Group2"}]
            }
        }
        mock_ops_mgr.find_automations = AsyncMock(return_value=[automation])
        mock_ops_mgr.get_automation = AsyncMock(return_value=automation)
        mock_ops_mgr.update_automation = AsyncMock(return_value=automation)

        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)
        resource.get_groups = AsyncMock(return_value={
            "Group1": {"_id": "1", "name": "Group1"},
            "Group2": {"_id": "2", "name": "Group2"},
            "Group3": {"_id": "3", "name": "Group3"}
        })

        await resource.set_gbac(
            "TestAutomation",
            read_groups=["Group3"],
            write_groups=None,
            preserve_read_groups=True,
            preserve_write_groups=True
        )

        # Verify update was called
        call_args = mock_ops_mgr.update_automation.call_args
        updated_automation = call_args[0][0]

        # Should have both original and new groups
        assert len(updated_automation["gbac"]["read"]) == 2
        assert len(updated_automation["gbac"]["write"]) == 1

    @pytest.mark.asyncio
    async def test_set_gbac_clears_groups_when_not_preserving(self):
        """Test set_gbac clears existing groups when preserve flags are False.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()

        automation = {
            "_id": "auto123",
            "name": "TestAutomation",
            "gbac": {
                "read": [{"_id": "1", "name": "Group1"}],
                "write": [{"_id": "2", "name": "Group2"}]
            }
        }
        mock_ops_mgr.find_automations = AsyncMock(return_value=[automation])
        mock_ops_mgr.get_automation = AsyncMock(return_value=automation)
        mock_ops_mgr.update_automation = AsyncMock(return_value=automation)

        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)
        resource.get_groups = AsyncMock(return_value={
            "Group1": {"_id": "1", "name": "Group1"},
            "Group2": {"_id": "2", "name": "Group2"},
            "Group3": {"_id": "3", "name": "Group3"}
        })

        await resource.set_gbac(
            "TestAutomation",
            read_groups=["Group3"],
            write_groups=None,
            preserve_read_groups=False,
            preserve_write_groups=False
        )

        # Verify update was called
        call_args = mock_ops_mgr.update_automation.call_args
        updated_automation = call_args[0][0]

        # Should only have new groups (existing cleared)
        assert len(updated_automation["gbac"]["read"]) == 1
        assert updated_automation["gbac"]["read"][0]["name"] == "Group3"
        assert len(updated_automation["gbac"]["write"]) == 0

    @pytest.mark.asyncio
    async def test_set_gbac_raises_for_nonexistent_automation(self):
        """Test set_gbac raises error when automation not found.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()
        mock_ops_mgr.find_automations = AsyncMock(return_value=[])

        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.set_gbac(
                "NonExistentAutomation",
                read_groups=["Group1"]
            )

        assert "Could not find automation" in str(exc_info.value)
        assert "NonExistentAutomation" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_set_gbac_raises_for_missing_groups(self):
        """Test set_gbac raises error when specified groups don't exist.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()

        automation = {
            "_id": "auto123",
            "name": "TestAutomation",
            "gbac": {
                "read": [],
                "write": []
            }
        }
        mock_ops_mgr.find_automations = AsyncMock(return_value=[automation])
        mock_ops_mgr.get_automation = AsyncMock(return_value=automation)

        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)
        resource.get_groups = AsyncMock(return_value={
            "Group1": {"_id": "1", "name": "Group1"}
        })

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.set_gbac(
                "TestAutomation",
                read_groups=["MissingGroup"]
            )

        assert "MissingGroup" in str(exc_info.value)
        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_set_gbac_no_changes_early_return(self):
        """Test set_gbac returns early when no changes requested.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()

        automation = {
            "_id": "auto123",
            "name": "TestAutomation",
            "gbac": {
                "read": [{"_id": "1", "name": "Group1"}],
                "write": []
            }
        }
        mock_ops_mgr.find_automations = AsyncMock(return_value=[automation])

        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)

        result = await resource.set_gbac(
            "TestAutomation",
            read_groups=None,
            write_groups=None,
            preserve_read_groups=True,
            preserve_write_groups=True
        )

        # Should return automation without calling update
        assert result == automation
        # update_automation should NOT be called
        assert not mock_ops_mgr.update_automation.called

    @pytest.mark.asyncio
    async def test_set_gbac_validates_preserved_groups_exist(self):
        """Test set_gbac validates that preserved groups still exist on server.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()

        # Automation has a group that no longer exists on server
        automation = {
            "_id": "auto123",
            "name": "TestAutomation",
            "gbac": {
                "read": [{"_id": "1", "name": "DeletedGroup"}],
                "write": []
            }
        }
        mock_ops_mgr.find_automations = AsyncMock(return_value=[automation])
        mock_ops_mgr.get_automation = AsyncMock(return_value=automation)

        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)
        # Server only has Group1, not DeletedGroup
        resource.get_groups = AsyncMock(return_value={
            "Group1": {"_id": "1", "name": "Group1"}
        })

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.set_gbac(
                "TestAutomation",
                read_groups=["Group1"],
                write_groups=None,
                preserve_read_groups=True,  # Try to preserve DeletedGroup
                preserve_write_groups=False
            )

        assert "DeletedGroup" in str(exc_info.value)
        assert "missing" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_set_gbac_adds_multiple_groups(self):
        """Test set_gbac can add multiple groups at once.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_ops_mgr = MagicMock()

        automation = {
            "_id": "auto123",
            "name": "TestAutomation",
            "gbac": {
                "read": [],
                "write": []
            }
        }
        mock_ops_mgr.find_automations = AsyncMock(return_value=[automation])
        mock_ops_mgr.get_automation = AsyncMock(return_value=automation)
        mock_ops_mgr.update_automation = AsyncMock(return_value=automation)

        mock_client.operations_manager = mock_ops_mgr

        resource = Resource(mock_client)
        resource.get_groups = AsyncMock(return_value={
            "Group1": {"_id": "1", "name": "Group1"},
            "Group2": {"_id": "2", "name": "Group2"},
            "Group3": {"_id": "3", "name": "Group3"},
            "Group4": {"_id": "4", "name": "Group4"}
        })

        await resource.set_gbac(
            "TestAutomation",
            read_groups=["Group1", "Group2"],
            write_groups=["Group3", "Group4"],
            preserve_read_groups=False,
            preserve_write_groups=False
        )

        # Verify update was called with all groups
        call_args = mock_ops_mgr.update_automation.call_args
        updated_automation = call_args[0][0]

        assert len(updated_automation["gbac"]["read"]) == 2
        assert len(updated_automation["gbac"]["write"]) == 2
        read_names = {g["name"] for g in updated_automation["gbac"]["read"]}
        write_names = {g["name"] for g in updated_automation["gbac"]["write"]}
        assert read_names == {"Group1", "Group2"}
        assert write_names == {"Group3", "Group4"}

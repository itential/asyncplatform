# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.resources.lifecycle_manager module."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from asyncplatform import exceptions
from asyncplatform.resources.lifecycle_manager import Resource


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
        assert Resource.name == "lifecycle_manager"

    def test_resource_lifecycle_manager_property(self):
        """Test that lifecycle_manager property returns client's lifecycle_manager service.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        assert resource.lifecycle_manager is mock_lm


class TestCheckIfResourceExists:
    """Test suite for _check_if_resource_exists method."""

    @pytest.mark.asyncio
    async def test_check_if_resource_exists_returns_true(self):
        """Test that _check_if_resource_exists returns True when resource exists.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(
            return_value=[{"_id": "res1", "name": "TestResource"}]
        )
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        result = await resource._check_if_resource_exists("TestResource")

        assert result is True
        mock_lm.get_resources.assert_called_once_with(
            **{"equals[name]": "TestResource"}
        )

    @pytest.mark.asyncio
    async def test_check_if_resource_exists_returns_false_when_empty(self):
        """Test that _check_if_resource_exists returns False when no resources returned.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(return_value=[])
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        result = await resource._check_if_resource_exists("NonExistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_check_if_resource_exists_returns_false_for_name_mismatch(self):
        """Test that _check_if_resource_exists returns False when names don't match exactly.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(
            return_value=[{"_id": "res1", "name": "TestResourceOther"}]
        )
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        result = await resource._check_if_resource_exists("TestResource")

        assert result is False


class TestEnsureResourceIsNew:
    """Test suite for _ensure_resource_is_new method."""

    @pytest.mark.asyncio
    async def test_ensure_resource_is_new_succeeds(self):
        """Test _ensure_resource_is_new succeeds when resource doesn't exist.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(return_value=[])
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)

        # Should not raise exception
        await resource._ensure_resource_is_new("NewResource")

    @pytest.mark.asyncio
    async def test_ensure_resource_is_new_raises_error(self):
        """Test _ensure_resource_is_new raises error when resource exists.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(
            return_value=[{"_id": "res1", "name": "ExistingResource"}]
        )
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource._ensure_resource_is_new("ExistingResource")

        assert "already exists" in str(exc_info.value)
        assert "ExistingResource" in str(exc_info.value)


class TestGetResourceById:
    """Test suite for get_resource_by_id method."""

    @pytest.mark.asyncio
    async def test_get_resource_by_id_returns_resource(self):
        """Test get_resource_by_id returns resource data from the service.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        expected = {"_id": "res123", "name": "MyResource"}
        mock_lm.get_resource = AsyncMock(return_value=expected)
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        result = await resource.get_resource_by_id("res123")

        assert result == expected
        mock_lm.get_resource.assert_called_once_with("res123")

    @pytest.mark.asyncio
    async def test_get_resource_by_id_passes_id_correctly(self):
        """Test get_resource_by_id passes the given ID to the service.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resource = AsyncMock(return_value={"_id": "abc", "name": "Res"})
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        await resource.get_resource_by_id("abc")

        mock_lm.get_resource.assert_called_once_with("abc")


class TestGetResourceByName:
    """Test suite for get_resource_by_name method."""

    @pytest.mark.asyncio
    async def test_get_resource_by_name_found(self):
        """Test get_resource_by_name returns resource when exact match found.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(
            return_value=[{"_id": "res123", "name": "TargetResource"}]
        )
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        result = await resource.get_resource_by_name("TargetResource")

        assert result == {"_id": "res123", "name": "TargetResource"}
        mock_lm.get_resources.assert_called_once_with(
            **{"equals[name]": "TargetResource"}
        )

    @pytest.mark.asyncio
    async def test_get_resource_by_name_not_found(self):
        """Test get_resource_by_name returns None when no match found.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(return_value=[])
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        result = await resource.get_resource_by_name("NonExistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_resource_by_name_exact_match_only(self):
        """Test get_resource_by_name returns only exact name match.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(
            return_value=[
                {"_id": "res1", "name": "Target"},
                {"_id": "res2", "name": "TargetResource"},
                {"_id": "res3", "name": "TargetOther"},
            ]
        )
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        result = await resource.get_resource_by_name("TargetResource")

        assert result == {"_id": "res2", "name": "TargetResource"}

    @pytest.mark.asyncio
    async def test_get_resource_by_name_returns_none_for_name_mismatch(self):
        """Test get_resource_by_name returns None when API returns non-matching names.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(
            return_value=[{"_id": "res1", "name": "OtherResource"}]
        )
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        result = await resource.get_resource_by_name("TargetResource")

        assert result is None


class TestImporter:
    """Test suite for importer method."""

    @pytest.mark.asyncio
    async def test_importer_success(self):
        """Test importer successfully imports a resource model.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(return_value=[])
        mock_lm.import_resource = AsyncMock(
            return_value={"_id": "new_res", "name": "TestResource"}
        )
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)

        resource_data = {"name": "TestResource", "description": "A test resource"}
        result = await resource.importer(resource_data)

        assert result["_id"] == "new_res"
        assert result["name"] == "TestResource"
        mock_lm.import_resource.assert_called_once_with(resource_data)

    @pytest.mark.asyncio
    async def test_importer_returns_imported_result(self):
        """Test importer returns the result from the service call.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(return_value=[])
        expected = {"_id": "res999", "name": "MyRes", "schema": {}}
        mock_lm.import_resource = AsyncMock(return_value=expected)
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        result = await resource.importer({"name": "MyRes"})

        assert result == expected

    @pytest.mark.asyncio
    async def test_importer_uses_result_name_for_logging(self):
        """Test importer works when result has different name than input data.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(return_value=[])
        mock_lm.import_resource = AsyncMock(
            return_value={"_id": "res1", "name": "NormalizedName"}
        )
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        result = await resource.importer({"name": "OriginalName"})

        # Should not raise and should return the service result
        assert result["name"] == "NormalizedName"


class TestDelete:
    """Test suite for delete method."""

    @pytest.mark.asyncio
    async def test_delete_success(self):
        """Test delete successfully deletes resource model by name.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(
            return_value=[{"_id": "res123", "name": "TargetResource"}]
        )
        mock_lm.delete_resource = AsyncMock(
            return_value={"message": "Successfully deleted"}
        )
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        result = await resource.delete("TargetResource")

        assert result == {"message": "Successfully deleted"}
        mock_lm.delete_resource.assert_called_once_with("res123")

    @pytest.mark.asyncio
    async def test_delete_not_found_returns_none(self):
        """Test delete returns None when resource model not found.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(return_value=[])
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        result = await resource.delete("NonExistent")

        assert result is None
        mock_lm.delete_resource.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_uses_resource_id(self):
        """Test delete passes the resource's _id to the service delete call.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(
            return_value=[{"_id": "abc-xyz", "name": "Resource"}]
        )
        mock_lm.delete_resource = AsyncMock(return_value={})
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        await resource.delete("Resource")

        mock_lm.delete_resource.assert_called_once_with("abc-xyz")


class TestValidateActions:
    """Test suite for validate_actions method."""

    @pytest.mark.asyncio
    async def test_validate_actions_success(self):
        """Test validate_actions succeeds when resource model is found.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(
            return_value=[{"_id": "res123", "name": "MyModel"}]
        )
        validation_result = {"valid": True, "errors": []}
        mock_lm.validate_actions = AsyncMock(return_value=validation_result)
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        actions = {"create": {"type": "script"}}
        result = await resource.validate_actions("MyModel", actions)

        assert result == validation_result
        mock_lm.validate_actions.assert_called_once_with("res123", actions)

    @pytest.mark.asyncio
    async def test_validate_actions_raises_when_model_not_found(self):
        """Test validate_actions raises error when resource model is not found.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(return_value=[])
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.validate_actions("NonExistentModel", {})

        assert "not found" in str(exc_info.value)
        assert "NonExistentModel" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_actions_passes_actions_to_service(self):
        """Test validate_actions passes the correct actions dict to the service.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(
            return_value=[{"_id": "res1", "name": "Model"}]
        )
        mock_lm.validate_actions = AsyncMock(return_value={"valid": True})
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        actions = {"create": {"type": "script"}, "delete": {"type": "api"}}
        await resource.validate_actions("Model", actions)

        mock_lm.validate_actions.assert_called_once_with("res1", actions)

    @pytest.mark.asyncio
    async def test_validate_actions_does_not_call_service_when_model_missing(self):
        """Test validate_actions does not call the service when the model is not found.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(return_value=[])
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)

        with pytest.raises(exceptions.AsyncPlatformError):
            await resource.validate_actions("Missing", {"action": {}})

        mock_lm.validate_actions.assert_not_called()


class TestImportInstance:
    """Test suite for import_instance method."""

    @pytest.mark.asyncio
    async def test_import_instance_success(self):
        """Test import_instance successfully imports instance into model.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(
            return_value=[{"_id": "res123", "name": "MyModel"}]
        )
        instance_result = {"_id": "inst1", "name": "MyInstance"}
        mock_lm.import_instance = AsyncMock(return_value=instance_result)
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        instance_data = {"name": "MyInstance", "value": "data"}
        result = await resource.import_instance("MyModel", instance_data)

        assert result == instance_result
        mock_lm.import_instance.assert_called_once_with("res123", instance_data)

    @pytest.mark.asyncio
    async def test_import_instance_raises_when_model_not_found(self):
        """Test import_instance raises error when resource model is not found.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(return_value=[])
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.import_instance("NonExistentModel", {"name": "inst"})

        assert "not found" in str(exc_info.value)
        assert "NonExistentModel" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_import_instance_does_not_call_service_when_model_missing(self):
        """Test import_instance does not call import when model is not found.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(return_value=[])
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)

        with pytest.raises(exceptions.AsyncPlatformError):
            await resource.import_instance("Missing", {"name": "inst"})

        mock_lm.import_instance.assert_not_called()

    @pytest.mark.asyncio
    async def test_import_instance_passes_model_id_and_instance_data(self):
        """Test import_instance passes the model _id and instance_data to the service.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(
            return_value=[{"_id": "model-id-99", "name": "Model"}]
        )
        mock_lm.import_instance = AsyncMock(return_value={"_id": "inst99", "name": "I"})
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        instance_data = {"name": "I", "field": "value"}
        await resource.import_instance("Model", instance_data)

        mock_lm.import_instance.assert_called_once_with("model-id-99", instance_data)

    @pytest.mark.asyncio
    async def test_import_instance_returns_service_result(self):
        """Test import_instance returns the full result from the service.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_lm = MagicMock()
        mock_lm.get_resources = AsyncMock(
            return_value=[{"_id": "res1", "name": "Model"}]
        )
        expected = {"_id": "inst1", "name": "Instance", "extra_field": "extra"}
        mock_lm.import_instance = AsyncMock(return_value=expected)
        mock_client.lifecycle_manager = mock_lm

        resource = Resource(mock_client)
        result = await resource.import_instance("Model", {"name": "Instance"})

        assert result == expected

# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.resources.configuration_manager module."""

import copy

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from asyncplatform import exceptions
from asyncplatform.resources.configuration_manager import Resource


class TestResourceInit:
    """Test suite for Resource initialization."""

    def test_resource_initialization(self):
        """Test that Resource initializes correctly with a client."""
        mock_client = MagicMock()
        resource = Resource(mock_client)

        assert resource.client is mock_client

    def test_resource_name_attribute(self):
        """Test that Resource has correct name attribute."""
        assert hasattr(Resource, "name")
        assert Resource.name == "configuration_manager"

    def test_resource_configuration_manager_property(self):
        """Test that configuration_manager property returns client's service."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)
        assert resource.configuration_manager is mock_cm


class TestCheckIfGoldenConfigExists:
    """Test suite for check_if_golden_config_exists method."""

    @pytest.mark.asyncio
    async def test_returns_true_when_config_exists(self):
        """Test returns True when a matching Golden Config tree is found."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(
            return_value=[{"_id": "tree1", "name": "Cisco Edge - Day 0"}]
        )
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)
        result = await resource.check_if_golden_config_exists("Cisco Edge - Day 0")

        assert result is True
        mock_cm.find_golden_configs.assert_called_once_with(name="Cisco Edge - Day 0")

    @pytest.mark.asyncio
    async def test_returns_false_when_config_not_found(self):
        """Test returns False when no matching Golden Config tree is found."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(return_value=[])
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)
        result = await resource.check_if_golden_config_exists("NonExistent Tree")

        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_when_api_returns_empty(self):
        """Test returns False when the API returns an empty list."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(return_value=[])
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)
        result = await resource.check_if_golden_config_exists("Any Tree")

        assert result is False


class TestEnsureGoldenConfigIsNew:
    """Test suite for _ensure_golden_config_is_new method."""

    @pytest.mark.asyncio
    async def test_succeeds_when_config_does_not_exist(self):
        """Test passes without raising when config does not exist."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(return_value=[])
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)

        # Should not raise
        await resource._ensure_golden_config_is_new("New Tree")

    @pytest.mark.asyncio
    async def test_raises_when_config_already_exists(self):
        """Test raises AsyncPlatformError when a config with the name already exists."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(
            return_value=[{"_id": "tree1", "name": "Existing Tree"}]
        )
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource._ensure_golden_config_is_new("Existing Tree")

        assert "already exists" in str(exc_info.value)
        assert "Existing Tree" in str(exc_info.value)


class TestGetGoldenConfigByName:
    """Test suite for get_golden_config_by_name method."""

    @pytest.mark.asyncio
    async def test_returns_config_when_found(self):
        """Test returns the matching config dict when an exact name match exists."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        expected = {"_id": "tree1", "name": "Cisco Edge - Day 0"}
        mock_cm.find_golden_configs = AsyncMock(return_value=[expected])
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)
        result = await resource.get_golden_config_by_name("Cisco Edge - Day 0")

        assert result == expected
        mock_cm.find_golden_configs.assert_called_once_with(name="Cisco Edge - Day 0")

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        """Test returns None when no config with the given name exists."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(return_value=[])
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)
        result = await resource.get_golden_config_by_name("NonExistent Tree")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_exact_name_match_only(self):
        """Test returns only the config with an exact name match."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(
            return_value=[
                {"_id": "tree1", "name": "Cisco Edge"},
                {"_id": "tree2", "name": "Cisco Edge - Day 0"},
                {"_id": "tree3", "name": "Cisco Edge - Day 1"},
            ]
        )
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)
        result = await resource.get_golden_config_by_name("Cisco Edge - Day 0")

        assert result == {"_id": "tree2", "name": "Cisco Edge - Day 0"}

    @pytest.mark.asyncio
    async def test_returns_none_when_api_returns_non_matching_names(self):
        """Test returns None when API results contain no exact name match."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(
            return_value=[{"_id": "tree1", "name": "Cisco Core - Day 0"}]
        )
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)
        result = await resource.get_golden_config_by_name("Cisco Edge - Day 0")

        assert result is None


class TestDelete:
    """Test suite for delete method."""

    @pytest.mark.asyncio
    async def test_delete_calls_service_with_config_id(self):
        """Test delete finds the config and calls delete_golden_config with its ID."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(
            return_value=[{"id": "tree-abc", "name": "Cisco Edge - Day 0"}]
        )
        mock_cm.delete_golden_config = AsyncMock(
            return_value={"status": "success", "deleted": 1}
        )
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)
        await resource.delete("Cisco Edge - Day 0")

        mock_cm.delete_golden_config.assert_called_once_with("tree-abc")

    @pytest.mark.asyncio
    async def test_delete_does_nothing_when_not_found(self):
        """Test delete does not call the service when config is not found."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(return_value=[])
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)
        await resource.delete("NonExistent Tree")

        mock_cm.delete_golden_config.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_uses_id_field(self):
        """Test delete uses the id field from the found config."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(
            return_value=[{"id": "abc-xyz-123", "name": "MyTree"}]
        )
        mock_cm.delete_golden_config = AsyncMock(return_value={})
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)
        await resource.delete("MyTree")

        mock_cm.delete_golden_config.assert_called_once_with("abc-xyz-123")


class TestImporter:
    """Test suite for importer method."""

    @pytest.mark.asyncio
    async def test_importer_success(self):
        """Test importer successfully imports trees when no duplicates exist."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(return_value=[])
        mock_cm.import_golden_config = AsyncMock(
            return_value={
                "status": "success",
                "message": "1 golden config trees imported",
            }
        )
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)

        trees = [{"data": [{"name": "Cisco Edge - Day 0", "version": "1.0"}]}]
        result = await resource.importer(trees)

        assert result["status"] == "success"
        mock_cm.import_golden_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_importer_raises_when_tree_already_exists(self):
        """Test importer raises AsyncPlatformError when a tree with same name exists."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(
            return_value=[{"_id": "tree1", "name": "Cisco Edge - Day 0"}]
        )
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)

        trees = [{"data": [{"name": "Cisco Edge - Day 0", "version": "1.0"}]}]

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.importer(trees)

        assert "already exists" in str(exc_info.value)
        assert "Cisco Edge - Day 0" in str(exc_info.value)
        mock_cm.import_golden_config.assert_not_called()

    @pytest.mark.asyncio
    async def test_importer_does_not_mutate_input(self):
        """Test importer deep-copies trees so the caller's data is not modified."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(return_value=[])
        mock_cm.import_golden_config = AsyncMock(
            return_value={"status": "success", "message": "imported"}
        )
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)

        original_trees = [{"data": [{"name": "Tree A", "version": "1.0"}]}]
        original_copy = copy.deepcopy(original_trees)

        await resource.importer(original_trees)

        assert original_trees == original_copy

    @pytest.mark.asyncio
    async def test_importer_passes_options_to_service(self):
        """Test importer forwards options to the service call."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(return_value=[])
        mock_cm.import_golden_config = AsyncMock(
            return_value={"status": "success", "message": "imported"}
        )
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)

        trees = [{"data": [{"name": "Tree A"}]}]
        options = {"overwrite": True}
        await resource.importer(trees, options=options)

        mock_cm.import_golden_config.assert_called_once_with(trees, options=options)

    @pytest.mark.asyncio
    async def test_importer_checks_all_trees_before_importing(self):
        """Test importer checks existence for every tree before calling import."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        # First call (Tree A) returns empty, second call (Tree B) returns a match
        mock_cm.find_golden_configs = AsyncMock(
            side_effect=[
                [],
                [{"_id": "tree2", "name": "Tree B"}],
            ]
        )
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)

        trees = [
            {"data": [{"name": "Tree A"}]},
            {"data": [{"name": "Tree B"}]},
        ]

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            await resource.importer(trees)

        assert "Tree B" in str(exc_info.value)
        mock_cm.import_golden_config.assert_not_called()

    @pytest.mark.asyncio
    async def test_importer_returns_service_result(self):
        """Test importer returns the full result from the service."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.find_golden_configs = AsyncMock(return_value=[])
        expected = {
            "status": "success",
            "message": "2 golden config trees imported successfully",
        }
        mock_cm.import_golden_config = AsyncMock(return_value=expected)
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)

        trees = [
            {"data": [{"name": "Tree A"}]},
            {"data": [{"name": "Tree B"}]},
        ]
        result = await resource.importer(trees)

        assert result == expected


class TestImportGoldenConfig:
    """Test suite for import_golden_config method."""

    @pytest.mark.asyncio
    async def test_import_returns_service_result(self):
        """Test import_golden_config returns the full result from the service."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        expected = {
            "status": "success",
            "message": "1 golden config trees imported successfully",
        }
        mock_cm.import_golden_config = AsyncMock(return_value=expected)
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)
        trees = [{"data": [{"name": "Tree A"}]}]
        result = await resource.import_golden_config(trees)

        assert result == expected

    @pytest.mark.asyncio
    async def test_import_forwards_trees_to_service(self):
        """Test import_golden_config passes trees to the service."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.import_golden_config = AsyncMock(
            return_value={"status": "success", "message": "imported"}
        )
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)
        trees = [{"data": [{"name": "Tree A"}]}, {"data": [{"name": "Tree B"}]}]
        await resource.import_golden_config(trees)

        mock_cm.import_golden_config.assert_called_once_with(trees, options=None)

    @pytest.mark.asyncio
    async def test_import_forwards_options_to_service(self):
        """Test import_golden_config passes options kwarg to the service."""
        mock_client = MagicMock()
        mock_cm = MagicMock()
        mock_cm.import_golden_config = AsyncMock(
            return_value={"status": "success", "message": "imported"}
        )
        mock_client.configuration_manager = mock_cm

        resource = Resource(mock_client)
        trees = [{"data": [{"name": "Tree A"}]}]
        options = {"overwrite": True}
        await resource.import_golden_config(trees, options=options)

        mock_cm.import_golden_config.assert_called_once_with(trees, options=options)

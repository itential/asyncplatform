# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.services.operations_manager module."""

from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asyncplatform import context
from asyncplatform.services.operations_manager import Service


class TestOperationsManagerServiceInitialization:
    """Test suite for Operations Manager Service initialization."""

    def test_service_has_name_attribute(self):
        """Test Service has name attribute.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert hasattr(Service, "name")
        assert Service.name == "operations_manager"

    def test_service_init_with_context(self):
        """Test Service initialization with context.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        service = Service(ctx)

        assert service.ctx is ctx


class TestOperationsManagerFindAutomations:
    """Test suite for find_automations method."""

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_find_automations_returns_list(self, mock_get):
        """Test find_automations returns list of automations.

        Args:
            mock_get: Mock for Service.get method

        Returns:
            None

        Raises:
            None
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            "metadata": {"total": 2},
            "data": [
                {"_id": "1", "name": "Automation1", "componentType": "workflows"},
                {"_id": "2", "name": "Automation2", "componentType": "workflows"},
            ],
        }
        mock_get.return_value = mock_response

        ctx = context.Context()
        service = Service(ctx)

        result = await service.find_automations()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "Automation1"

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_find_automations_returns_empty_list_when_no_automations(
        self, mock_get
    ):
        """Test find_automations returns empty list when no automations exist.

        Args:
            mock_get: Mock for Service.get method

        Returns:
            None

        Raises:
            None
        """
        mock_response = Mock()
        mock_response.json.return_value = {"metadata": {"total": 0}, "data": []}
        mock_get.return_value = mock_response

        ctx = context.Context()
        service = Service(ctx)

        result = await service.find_automations()

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_find_automations_with_name_filter(self, mock_get):
        """Test find_automations with name parameter.

        Args:
            mock_get: Mock for Service.get method

        Returns:
            None

        Raises:
            None
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            "metadata": {"total": 1},
            "data": [{"_id": "1", "name": "SpecificAutomation"}],
        }
        mock_get.return_value = mock_response

        ctx = context.Context()
        service = Service(ctx)

        result = await service.find_automations(name="SpecificAutomation")

        assert len(result) == 1
        assert result[0]["name"] == "SpecificAutomation"

        # Verify params were passed correctly
        call_args = mock_get.call_args
        assert call_args[1]["params"]["equalsField"] == "name"
        assert call_args[1]["params"]["equals"] == "SpecificAutomation"

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_find_automations_without_name_filter(self, mock_get):
        """Test find_automations without name parameter.

        Args:
            mock_get: Mock for Service.get method

        Returns:
            None

        Raises:
            None
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            "metadata": {"total": 3},
            "data": [
                {"_id": "1", "name": "Automation1"},
                {"_id": "2", "name": "Automation2"},
                {"_id": "3", "name": "Automation3"},
            ],
        }
        mock_get.return_value = mock_response

        ctx = context.Context()
        service = Service(ctx)

        result = await service.find_automations()

        assert len(result) == 3

        # Verify params don't include name filter
        call_args = mock_get.call_args
        assert "equalsField" not in call_args[1]["params"]
        assert "equals" not in call_args[1]["params"]

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_find_automations_handles_pagination(self, mock_get):
        """Test find_automations handles multiple pages.

        Args:
            mock_get: Mock for Service.get method

        Returns:
            None

        Raises:
            None
        """
        # First page - needs response with .json() method
        mock_response1 = Mock()
        mock_response1.json.return_value = {
            "metadata": {"total": 250},
            "data": [{"_id": f"{i}", "name": f"Automation{i}"} for i in range(100)],
        }

        # Subsequent pages - return dict directly for pagination
        page2 = {
            "metadata": {"total": 250},
            "data": [
                {"_id": f"{i}", "name": f"Automation{i}"} for i in range(100, 200)
            ],
        }

        page3 = {
            "metadata": {"total": 250},
            "data": [
                {"_id": f"{i}", "name": f"Automation{i}"} for i in range(200, 250)
            ],
        }

        mock_get.side_effect = [mock_response1, page2, page3]

        ctx = context.Context()
        service = Service(ctx)

        result = await service.find_automations()

        assert len(result) == 250
        assert result[0]["name"] == "Automation0"
        assert result[249]["name"] == "Automation249"

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_find_automations_handles_pagination_with_exception(self, mock_get):
        """Test find_automations propagates exceptions during pagination.

        Args:
            mock_get: Mock for Service.get method

        Returns:
            None

        Raises:
            None
        """
        # First page succeeds - needs response with .json() method
        mock_response1 = Mock()
        mock_response1.json.return_value = {
            "metadata": {"total": 250},
            "data": [{"_id": f"{i}", "name": f"Automation{i}"} for i in range(100)],
        }

        # Second page raises exception
        mock_get.side_effect = [mock_response1, Exception("API error")]

        ctx = context.Context()
        service = Service(ctx)

        with pytest.raises(Exception) as exc_info:
            await service.find_automations()

        assert "API error" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_find_automations_limit_exactly_equals_total(self, mock_get):
        """Test find_automations when total equals limit.

        Args:
            mock_get: Mock for Service.get method

        Returns:
            None

        Raises:
            None
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            "metadata": {"total": 100},
            "data": [{"_id": f"{i}", "name": f"Automation{i}"} for i in range(100)],
        }
        mock_get.return_value = mock_response

        ctx = context.Context()
        service = Service(ctx)

        result = await service.find_automations()

        # Should only call get once (no pagination needed)
        assert mock_get.call_count == 1
        assert len(result) == 100


class TestOperationsManagerImportAutomation:
    """Test suite for import_automation method."""

    @pytest.mark.asyncio
    async def test_import_automation_success(self):
        """Test import_automation successfully imports automation.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "message": "Successfully imported automation",
            "data": [
                {
                    "data": {
                        "_id": "automation123",
                        "name": "TestAutomation",
                        "componentType": "workflows",
                    }
                }
            ],
        }
        mock_client.put = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        automation_data = {
            "name": "TestAutomation",
            "description": "Test automation description",
            "componentName": "TestWorkflow",
            "componentType": "workflows",
            "componentId": "workflow123",
        }

        result = await service.import_automation(automation_data)

        assert result is not None
        assert result["_id"] == "automation123"
        assert result["name"] == "TestAutomation"

        # Verify put was called with correct path and payload
        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args
        assert call_args[0][0] == "/operations-manager/automations"
        assert call_args[1]["json"]["automations"][0] == automation_data

    @pytest.mark.asyncio
    async def test_import_automation_preserves_input(self):
        """Test import_automation doesn't mutate input automation data.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "message": "Success",
            "data": [{"data": {"_id": "auto1", "name": "TestAutomation"}}],
        }
        mock_client.put = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        automation_data = {"name": "TestAutomation", "componentType": "workflows"}
        original_data = automation_data.copy()

        await service.import_automation(automation_data)

        # Verify original data wasn't modified
        assert automation_data == original_data


class TestOperationsManagerDeleteAutomation:
    """Test suite for delete_automation method."""

    @pytest.mark.asyncio
    async def test_delete_automation_success(self):
        """Test delete_automation successfully deletes automation.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"message": "Successfully deleted automation"}
        mock_client.delete = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.delete_automation("automation123")

        assert result is not None
        assert "message" in result

        # Verify delete was called with correct path
        mock_client.delete.assert_called_once()
        call_args = mock_client.delete.call_args
        assert call_args[0][0] == "/operations-manager/automations/automation123"

    @pytest.mark.asyncio
    async def test_delete_automation_with_different_ids(self):
        """Test delete_automation with various automation IDs.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"message": "Deleted"}
        mock_client.delete = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        # Test with different ID formats
        test_ids = ["auto123", "automation_456", "workflow-789"]

        for test_id in test_ids:
            await service.delete_automation(test_id)
            call_args = mock_client.delete.call_args
            assert f"/operations-manager/automations/{test_id}" in call_args[0][0]


class TestOperationsManagerUpdateAutomation:
    """Test suite for update_automation method."""

    @pytest.mark.asyncio
    async def test_update_automation_success(self):
        """Test update_automation successfully updates automation.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "message": "Successfully updated automation",
            "data": {
                "_id": "automation123",
                "name": "UpdatedAutomation",
                "description": "Updated description",
            },
        }
        mock_client.patch = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        automation = {
            "_id": "automation123",
            "name": "UpdatedAutomation",
            "description": "Updated description",
        }

        result = await service.update_automation(automation)

        assert result is not None
        assert result["_id"] == "automation123"
        assert result["name"] == "UpdatedAutomation"

        # Verify patch was called with correct path and data
        mock_client.patch.assert_called_once()
        call_args = mock_client.patch.call_args
        assert call_args[0][0] == "/operations-manager/automations/automation123"
        assert call_args[1]["json"] == automation

    @pytest.mark.asyncio
    async def test_update_automation_passes_full_data(self):
        """Test update_automation passes complete automation data.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "message": "Updated",
            "data": {"_id": "auto1"},
        }
        mock_client.patch = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        automation_data = {
            "_id": "auto1",
            "name": "Test",
            "componentType": "workflows",
            "gbac": {"read": [], "write": []},
        }

        await service.update_automation(automation_data)

        # Verify the full automation object was passed
        call_args = mock_client.patch.call_args
        assert call_args[1]["json"] == automation_data


class TestOperationsManagerPaginationExceptions:
    """Test suite for exception handling in pagination."""

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_find_automations_handles_pagination_with_exception(self, mock_get):
        """Test find_automations propagates exceptions from paginated requests.

        Args:
            mock_get: Mock for Service.get method

        Returns:
            None

        Raises:
            None
        """
        # First page succeeds
        mock_response1 = Mock()
        mock_response1.json.return_value = {
            "metadata": {"total": 250},
            "data": [{"_id": f"{i}", "name": f"Automation{i}"} for i in range(100)],
        }

        # Second page raises exception
        mock_get.side_effect = [mock_response1, RuntimeError("Network error")]

        ctx = context.Context()
        service = Service(ctx)

        with pytest.raises(RuntimeError, match="Network error"):
            await service.find_automations()

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_find_automations_limit_exactly_equals_total(self, mock_get):
        """Test find_automations when total exactly equals limit.

        Args:
            mock_get: Mock for Service.get method

        Returns:
            None

        Raises:
            None
        """
        # Exactly 100 automations (matches limit)
        mock_response = Mock()
        mock_response.json.return_value = {
            "metadata": {"total": 100},
            "data": [{"_id": f"{i}", "name": f"Automation{i}"} for i in range(100)],
        }
        mock_get.return_value = mock_response

        ctx = context.Context()
        service = Service(ctx)

        result = await service.find_automations()

        # Should make only one request (no pagination needed)
        assert mock_get.call_count == 1
        assert len(result) == 100
        assert result[0]["name"] == "Automation0"
        assert result[99]["name"] == "Automation99"


class TestOperationsManagerIntegration:
    """Integration tests for Operations Manager Service."""

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_find_and_verify_single_automation(self, mock_get):
        """Test finding single automation with exact name match.

        Args:
            mock_get: Mock for Service.get method

        Returns:
            None

        Raises:
            None
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            "metadata": {"total": 1},
            "data": [
                {
                    "_id": "auto1",
                    "name": "TargetAutomation",
                    "componentType": "workflows",
                    "componentName": "TargetWorkflow",
                    "componentId": "wf123",
                }
            ],
        }
        mock_get.return_value = mock_response

        ctx = context.Context()
        service = Service(ctx)

        result = await service.find_automations(name="TargetAutomation")

        assert len(result) == 1
        assert result[0]["name"] == "TargetAutomation"
        assert result[0]["_id"] == "auto1"
        assert result[0]["componentType"] == "workflows"

    @pytest.mark.asyncio
    async def test_complete_automation_lifecycle(self):
        """Test complete lifecycle: import then delete.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = Mock()

        # Mock import response
        import_response = Mock()
        import_response.json.return_value = {
            "message": "Imported",
            "data": [{"data": {"_id": "new_auto", "name": "NewAutomation"}}],
        }

        # Mock delete response
        delete_response = Mock()
        delete_response.json.return_value = {"message": "Deleted"}

        mock_client.put = AsyncMock(return_value=import_response)
        mock_client.delete = AsyncMock(return_value=delete_response)
        ctx.client = mock_client

        service = Service(ctx)

        # Import automation
        automation_data = {"name": "NewAutomation", "componentType": "workflows"}
        import_result = await service.import_automation(automation_data)
        automation_id = import_result["_id"]

        # Delete automation
        delete_result = await service.delete_automation(automation_id)

        assert import_result["_id"] == "new_auto"
        assert "message" in delete_result

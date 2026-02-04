# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.services.lifecycle_manager module."""

from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asyncplatform import context
from asyncplatform.services.lifecycle_manager import Service


class TestLifecycleManagerServiceInitialization:
    """Test suite for Lifecycle Manager Service initialization."""

    def test_service_has_name_attribute(self):
        """Test Service has name attribute."""
        assert hasattr(Service, "name")
        assert Service.name == "lifecycle_manager"

    def test_service_has_pagination_limit(self):
        """Test Service has PAGINATION_LIMIT constant."""
        assert hasattr(Service, "PAGINATION_LIMIT")
        assert Service.PAGINATION_LIMIT == 100

    def test_service_init_with_context(self):
        """Test Service initialization with context."""
        ctx = context.Context()
        service = Service(ctx)

        assert service.ctx is ctx


class TestLifecycleManagerFetchAllPaginated:
    """Test suite for _fetch_all_paginated helper method."""

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_fetch_all_paginated_returns_empty_list_when_no_items(self, mock_get):
        """Test _fetch_all_paginated returns empty list when total is 0."""
        mock_response = Mock()
        mock_response.json.return_value = {"metadata": {"total": 0}, "data": []}
        mock_get.return_value = mock_response

        ctx = context.Context()
        service = Service(ctx)

        result = await service._fetch_all_paginated("/test-path")

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_fetch_all_paginated_returns_single_page(self, mock_get):
        """Test _fetch_all_paginated returns single page when total <= limit."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "metadata": {"total": 2},
            "data": [{"id": "1"}, {"id": "2"}],
        }
        mock_get.return_value = mock_response

        ctx = context.Context()
        service = Service(ctx)

        result = await service._fetch_all_paginated("/test-path")

        assert len(result) == 2
        assert result[0]["id"] == "1"
        mock_get.assert_called_once()

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_fetch_all_paginated_handles_items_key(self, mock_get):
        """Test _fetch_all_paginated handles 'items' key instead of 'data'."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "metadata": {"total": 2},
            "items": [{"id": "1"}, {"id": "2"}],
        }
        mock_get.return_value = mock_response

        ctx = context.Context()
        service = Service(ctx)

        result = await service._fetch_all_paginated("/test-path")

        assert len(result) == 2
        assert result[0]["id"] == "1"

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_fetch_all_paginated_handles_multiple_pages(self, mock_get):
        """Test _fetch_all_paginated handles pagination across multiple pages."""
        mock_response1 = Mock()
        mock_response1.json.return_value = {
            "metadata": {"total": 250},
            "data": [{"id": f"{i}"} for i in range(100)],
        }

        mock_response2 = Mock()
        mock_response2.json.return_value = {
            "metadata": {"total": 250},
            "data": [{"id": f"{i}"} for i in range(100, 200)],
        }

        mock_response3 = Mock()
        mock_response3.json.return_value = {
            "metadata": {"total": 250},
            "data": [{"id": f"{i}"} for i in range(200, 250)],
        }

        mock_get.side_effect = [mock_response1, mock_response2, mock_response3]

        ctx = context.Context()
        service = Service(ctx)

        result = await service._fetch_all_paginated("/test-path")

        assert len(result) == 250
        assert result[0]["id"] == "0"
        assert result[249]["id"] == "249"

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_fetch_all_paginated_propagates_exception(self, mock_get):
        """Test _fetch_all_paginated propagates exceptions from requests."""
        mock_response1 = Mock()
        mock_response1.json.return_value = {
            "metadata": {"total": 250},
            "data": [{"id": f"{i}"} for i in range(100)],
        }

        mock_get.side_effect = [mock_response1, RuntimeError("API error")]

        ctx = context.Context()
        service = Service(ctx)

        with pytest.raises(RuntimeError, match="API error"):
            await service._fetch_all_paginated("/test-path")

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_fetch_all_paginated_passes_filters(self, mock_get):
        """Test _fetch_all_paginated passes filter parameters correctly."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "metadata": {"total": 1},
            "data": [{"id": "1"}],
        }
        mock_get.return_value = mock_response

        ctx = context.Context()
        service = Service(ctx)

        await service._fetch_all_paginated(
            "/test-path", **{"equals[status]": "active", "sort": "name"}
        )

        call_args = mock_get.call_args
        assert call_args[1]["params"]["equals[status]"] == "active"
        assert call_args[1]["params"]["sort"] == "name"


class TestLifecycleManagerGetActionExecutions:
    """Test suite for get_action_executions method."""

    @pytest.mark.asyncio
    @patch.object(Service, "_fetch_all_paginated")
    async def test_get_action_executions_calls_helper(self, mock_fetch):
        """Test get_action_executions delegates to _fetch_all_paginated."""
        mock_fetch.return_value = [{"id": "1", "status": "completed"}]

        ctx = context.Context()
        service = Service(ctx)

        result = await service.get_action_executions()

        mock_fetch.assert_called_once_with("/lifecycle-manager/action-executions")
        assert len(result) == 1
        assert result[0]["status"] == "completed"

    @pytest.mark.asyncio
    @patch.object(Service, "_fetch_all_paginated")
    async def test_get_action_executions_passes_filters(self, mock_fetch):
        """Test get_action_executions passes filter parameters."""
        mock_fetch.return_value = []

        ctx = context.Context()
        service = Service(ctx)

        await service.get_action_executions(**{"equals[status]": "completed"})

        call_args = mock_fetch.call_args
        assert call_args[1]["equals[status]"] == "completed"


class TestLifecycleManagerGetActionExecution:
    """Test suite for get_action_execution method."""

    @pytest.mark.asyncio
    async def test_get_action_execution_returns_execution_data(self):
        """Test get_action_execution returns execution details."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "exec123",
            "status": "completed",
            "result": {"success": True},
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        result = await service.get_action_execution("exec123")

        assert result["id"] == "exec123"
        assert result["status"] == "completed"
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "/lifecycle-manager/action-executions/exec123"


class TestLifecycleManagerGetResources:
    """Test suite for get_resources method."""

    @pytest.mark.asyncio
    @patch.object(Service, "_fetch_all_paginated")
    async def test_get_resources_calls_helper(self, mock_fetch):
        """Test get_resources delegates to _fetch_all_paginated."""
        mock_fetch.return_value = [{"id": "1", "name": "NetworkDevice"}]

        ctx = context.Context()
        service = Service(ctx)

        result = await service.get_resources()

        mock_fetch.assert_called_once_with("/lifecycle-manager/resources")
        assert len(result) == 1
        assert result[0]["name"] == "NetworkDevice"

    @pytest.mark.asyncio
    @patch.object(Service, "_fetch_all_paginated")
    async def test_get_resources_passes_filters(self, mock_fetch):
        """Test get_resources passes filter parameters."""
        mock_fetch.return_value = []

        ctx = context.Context()
        service = Service(ctx)

        await service.get_resources(**{"contains[description]": "router"})

        call_args = mock_fetch.call_args
        assert call_args[1]["contains[description]"] == "router"


class TestLifecycleManagerCreateResource:
    """Test suite for create_resource method."""

    @pytest.mark.asyncio
    async def test_create_resource_returns_created_data(self):
        """Test create_resource returns created resource model."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "resource123",
            "name": "NetworkDevice",
            "schema": {},
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        resource_data = {"name": "NetworkDevice", "schema": {}}

        result = await service.create_resource(resource_data)

        assert result["id"] == "resource123"
        assert result["name"] == "NetworkDevice"


class TestLifecycleManagerGetResource:
    """Test suite for get_resource method."""

    @pytest.mark.asyncio
    async def test_get_resource_returns_resource_data(self):
        """Test get_resource returns resource model details."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "resource123",
            "name": "NetworkDevice",
            "schema": {"fields": []},
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        result = await service.get_resource("resource123")

        assert result["id"] == "resource123"
        assert result["name"] == "NetworkDevice"


class TestLifecycleManagerUpdateResource:
    """Test suite for update_resource method."""

    @pytest.mark.asyncio
    async def test_update_resource_returns_updated_data(self):
        """Test update_resource returns updated resource model."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "resource123",
            "name": "UpdatedDevice",
            "schema": {},
        }
        mock_client.put = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        update_data = {"name": "UpdatedDevice", "schema": {}}

        result = await service.update_resource("resource123", update_data)

        assert result["name"] == "UpdatedDevice"


class TestLifecycleManagerDeleteResource:
    """Test suite for delete_resource method."""

    @pytest.mark.asyncio
    async def test_delete_resource_returns_deletion_result(self):
        """Test delete_resource returns deletion result."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"message": "Resource deleted successfully"}
        mock_client.delete = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        result = await service.delete_resource("resource123")

        assert result["message"] == "Resource deleted successfully"


class TestLifecycleManagerEditResource:
    """Test suite for edit_resource method."""

    @pytest.mark.asyncio
    async def test_edit_resource_returns_edited_data(self):
        """Test edit_resource returns edited resource model."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "resource123",
            "name": "EditedDevice",
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        edits = {
            "operations": [{"op": "replace", "path": "/name", "value": "EditedDevice"}]
        }

        result = await service.edit_resource("resource123", edits)

        assert result["name"] == "EditedDevice"


class TestLifecycleManagerImportResource:
    """Test suite for import_resource method."""

    @pytest.mark.asyncio
    async def test_import_resource_returns_imported_data(self):
        """Test import_resource returns imported resource model."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "imported123",
            "name": "ImportedDevice",
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        resource_data = {"name": "ImportedDevice", "schema": {}}

        result = await service.import_resource(resource_data)

        assert result["id"] == "imported123"
        assert result["name"] == "ImportedDevice"


class TestLifecycleManagerExportResource:
    """Test suite for export_resource method."""

    @pytest.mark.asyncio
    async def test_export_resource_returns_exportable_data(self):
        """Test export_resource returns exportable resource model."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "resource123",
            "name": "NetworkDevice",
            "exportFormat": "v1",
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        result = await service.export_resource("resource123")

        assert result["id"] == "resource123"
        assert result["exportFormat"] == "v1"


class TestLifecycleManagerValidateActions:
    """Test suite for validate_actions method."""

    @pytest.mark.asyncio
    async def test_validate_actions_returns_validation_results(self):
        """Test validate_actions returns validation results."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "valid": True,
            "errors": [],
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        actions = {"provision": {"type": "workflow"}}

        result = await service.validate_actions("resource123", actions)

        assert result["valid"] is True
        assert len(result["errors"]) == 0


class TestLifecycleManagerRunAction:
    """Test suite for run_action method."""

    @pytest.mark.asyncio
    async def test_run_action_returns_execution_result(self):
        """Test run_action returns action execution result."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "executionId": "exec123",
            "status": "running",
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        action_data = {"actionName": "provision", "parameters": {}}

        result = await service.run_action("resource123", action_data)

        assert result["executionId"] == "exec123"
        assert result["status"] == "running"


class TestLifecycleManagerGetInstances:
    """Test suite for get_instances method."""

    @pytest.mark.asyncio
    @patch.object(Service, "_fetch_all_paginated")
    async def test_get_instances_calls_helper(self, mock_fetch):
        """Test get_instances delegates to _fetch_all_paginated."""
        mock_fetch.return_value = [{"id": "1", "name": "prod-router-01"}]

        ctx = context.Context()
        service = Service(ctx)

        result = await service.get_instances("model123")

        mock_fetch.assert_called_once_with(
            "/lifecycle-manager/resources/model123/instances"
        )
        assert len(result) == 1
        assert result[0]["name"] == "prod-router-01"

    @pytest.mark.asyncio
    @patch.object(Service, "_fetch_all_paginated")
    async def test_get_instances_passes_filters(self, mock_fetch):
        """Test get_instances passes filter parameters."""
        mock_fetch.return_value = []

        ctx = context.Context()
        service = Service(ctx)

        await service.get_instances("model123", **{"contains[ipAddress]": "10.0."})

        call_args = mock_fetch.call_args
        assert call_args[1]["contains[ipAddress]"] == "10.0."


class TestLifecycleManagerGetInstance:
    """Test suite for get_instance method."""

    @pytest.mark.asyncio
    async def test_get_instance_returns_instance_data(self):
        """Test get_instance returns instance details."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "instance123",
            "name": "prod-router-01",
            "ipAddress": "10.0.1.1",
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        result = await service.get_instance("model123", "instance123")

        assert result["id"] == "instance123"
        assert result["name"] == "prod-router-01"


class TestLifecycleManagerUpdateInstance:
    """Test suite for update_instance method."""

    @pytest.mark.asyncio
    async def test_update_instance_returns_updated_data(self):
        """Test update_instance returns updated instance."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "instance123",
            "name": "updated-router",
            "description": "Updated description",
        }
        mock_client.put = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        update_data = {"name": "updated-router", "description": "Updated description"}

        result = await service.update_instance("model123", "instance123", update_data)

        assert result["name"] == "updated-router"
        assert result["description"] == "Updated description"


class TestLifecycleManagerImportInstance:
    """Test suite for import_instance method."""

    @pytest.mark.asyncio
    async def test_import_instance_returns_imported_data(self):
        """Test import_instance returns imported instance."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "imported123",
            "name": "imported-router",
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        instance_data = {"name": "imported-router", "ipAddress": "10.0.1.1"}

        result = await service.import_instance("model123", instance_data)

        assert result["id"] == "imported123"
        assert result["name"] == "imported-router"


class TestLifecycleManagerExportInstance:
    """Test suite for export_instance method."""

    @pytest.mark.asyncio
    async def test_export_instance_returns_exportable_data(self):
        """Test export_instance returns exportable instance."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "instance123",
            "name": "prod-router-01",
            "exportFormat": "v1",
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        result = await service.export_instance("model123", "instance123")

        assert result["id"] == "instance123"
        assert result["exportFormat"] == "v1"

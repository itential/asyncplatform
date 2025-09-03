# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.services.automation_studio module."""

from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asyncplatform import context
from asyncplatform import exceptions
from asyncplatform.services.automation_studio import Service


class TestAutomationStudioServiceInitialization:
    """Test suite for Automation Studio Service initialization."""

    def test_service_has_name_attribute(self):
        """Test Service has name attribute."""
        assert hasattr(Service, "name")
        assert Service.name == "automation_studio"

    def test_service_init_with_context(self):
        """Test Service initialization with context."""
        ctx = context.Context()
        service = Service(ctx)

        assert service.ctx is ctx


class TestAutomationStudioGetProjects:
    """Test suite for get_projects method."""

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_get_projects_returns_list(self, mock_get):
        """Test get_projects returns list of projects."""
        mock_get.return_value = {
            "metadata": {"total": 2},
            "data": [
                {"_id": "1", "name": "Project1"},
                {"_id": "2", "name": "Project2"},
            ],
        }

        ctx = context.Context()
        service = Service(ctx)

        result = await service.get_projects()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "Project1"

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_get_projects_returns_empty_list_when_no_projects(self, mock_get):
        """Test get_projects returns empty list when no projects exist."""
        mock_get.return_value = {"metadata": {"total": 0}, "data": []}

        ctx = context.Context()
        service = Service(ctx)

        result = await service.get_projects()

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_get_projects_handles_pagination(self, mock_get):
        """Test get_projects handles multiple pages."""
        # First page
        page1 = {
            "metadata": {"total": 250},
            "data": [{"_id": f"{i}", "name": f"Project{i}"} for i in range(100)],
        }

        # Subsequent pages
        page2 = {
            "metadata": {"total": 250},
            "data": [{"_id": f"{i}", "name": f"Project{i}"} for i in range(100, 200)],
        }

        page3 = {
            "metadata": {"total": 250},
            "data": [{"_id": f"{i}", "name": f"Project{i}"} for i in range(200, 250)],
        }

        mock_get.side_effect = [page1, page2, page3]

        ctx = context.Context()
        service = Service(ctx)

        result = await service.get_projects()

        assert len(result) == 250
        assert result[0]["name"] == "Project0"
        assert result[249]["name"] == "Project249"

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_get_projects_handles_pagination_with_exception(self, mock_get):
        """Test get_projects propagates exceptions from paginated requests."""
        # First page succeeds
        page1 = {
            "metadata": {"total": 250},
            "data": [{"_id": f"{i}", "name": f"Project{i}"} for i in range(100)],
        }

        # Second page raises an exception
        mock_get.side_effect = [page1, RuntimeError("API error")]

        ctx = context.Context()
        service = Service(ctx)

        with pytest.raises(RuntimeError, match="API error"):
            await service.get_projects()

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_get_projects_limit_exactly_equals_total(self, mock_get):
        """Test get_projects when total exactly equals limit."""
        # Exactly 100 projects (matches limit)
        mock_get.return_value = {
            "metadata": {"total": 100},
            "data": [{"_id": f"{i}", "name": f"Project{i}"} for i in range(100)],
        }

        ctx = context.Context()
        service = Service(ctx)

        result = await service.get_projects()

        # Should make only one request (no pagination needed)
        assert mock_get.call_count == 1
        assert len(result) == 100
        assert result[0]["name"] == "Project0"
        assert result[99]["name"] == "Project99"


class TestAutomationStudioDescribeProject:
    """Test suite for describe_project method."""

    @pytest.mark.asyncio
    async def test_describe_project_returns_project_data(self):
        """Test describe_project returns project details."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "metadata": {"total": 1},
            "data": [
                {
                    "_id": "project123",
                    "name": "TestProject",
                    "description": "A test project",
                }
            ],
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.describe_project("project123")

        assert result is not None
        assert result["_id"] == "project123"
        assert result["name"] == "TestProject"

    @pytest.mark.asyncio
    async def test_describe_project_returns_none_when_not_found(self):
        """Test describe_project returns None when project not found."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"metadata": {"total": 0}, "data": []}
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.describe_project("nonexistent")

        assert result is None


class TestAutomationStudioFindProjects:
    """Test suite for find_projects method."""

    @pytest.mark.asyncio
    async def test_find_projects_with_name_filter(self):
        """Test find_projects with name parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "metadata": {"total": 1},
            "data": [{"_id": "1", "name": "TestProject"}],
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.find_projects(name="TestProject")

        assert len(result) == 1
        assert result[0]["name"] == "TestProject"

        # Verify params were passed correctly
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["equals[name]"] == "TestProject"

    @pytest.mark.asyncio
    async def test_find_projects_without_name_filter(self):
        """Test find_projects without name parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "metadata": {"total": 3},
            "data": [
                {"_id": "1", "name": "Project1"},
                {"_id": "2", "name": "Project2"},
                {"_id": "3", "name": "Project3"},
            ],
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.find_projects()

        assert len(result) == 3

        # Verify params dict is empty (no name filter)
        call_args = mock_client.get.call_args
        assert call_args[1]["params"] == {}


class TestAutomationStudioImportProject:
    """Test suite for import_project method."""

    @pytest.mark.asyncio
    async def test_import_project_returns_imported_data(self):
        """Test import_project returns imported project data."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "_id": "new_project_123",
                "name": "ImportedProject",
                "description": "Imported project",
            }
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        project_data = {"name": "ImportedProject", "description": "Imported project"}

        result = await service.import_project(project_data)

        assert result["_id"] == "new_project_123"
        assert result["name"] == "ImportedProject"

    @pytest.mark.asyncio
    async def test_import_project_passes_correct_params(self):
        """Test import_project passes correct parameters to API."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"_id": "123", "name": "Test"}}
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        project_data = {"name": "Test", "workflows": []}

        await service.import_project(project_data)

        # Verify correct endpoint and payload
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/automation-studio/projects/import"
        payload = call_args[1]["json"]
        assert payload["project"] == project_data
        assert payload["assignNewReferences"] is False
        assert payload["conflictMode"] == "insert-new"


class TestAutomationStudioDeleteProject:
    """Test suite for delete_project method."""

    @pytest.mark.asyncio
    async def test_delete_project_returns_deletion_result(self):
        """Test delete_project returns deletion result."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "message": "Project deleted successfully",
            "data": None,
            "metadata": {"deletedComponents": ["workflow1", "workflow2"]},
        }
        mock_client.delete = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.delete_project("project123")

        assert result["message"] == "Project deleted successfully"
        assert len(result["metadata"]["deletedComponents"]) == 2


class TestAutomationStudioPatchProject:
    """Test suite for patch_project method."""

    @pytest.mark.asyncio
    async def test_patch_project_updates_fields(self):
        """Test patch_project updates project fields."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_client.patch = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        update_data = {"name": "UpdatedName", "description": "Updated description"}

        result = await service.patch_project("project123", update_data)

        assert result is mock_response


class TestAutomationStudioDescribeWorkflow:
    """Test suite for describe_workflow method."""

    @pytest.mark.asyncio
    async def test_describe_workflow_returns_workflow_data(self):
        """Test describe_workflow returns workflow details."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [
                {"_id": "workflow123", "name": "TestWorkflow", "type": "automation"}
            ],
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.describe_workflow("workflow123")

        assert result["_id"] == "workflow123"
        assert result["name"] == "TestWorkflow"

    @pytest.mark.asyncio
    async def test_describe_workflow_raises_not_found_error(self):
        """Test describe_workflow raises NotFoundError when workflow not found."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"total": 0, "items": []}
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service.describe_workflow("nonexistent")

        assert "workflow id nonexistent not found" in str(exc_info.value)


class TestAutomationStudioFindWorkflows:
    """Test suite for find_workflows method."""

    @pytest.mark.asyncio
    async def test_find_workflows_without_filters(self):
        """Test find_workflows returns all workflows when no filters provided."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"_id": "wf1", "name": "Workflow1"},
                {"_id": "wf2", "name": "Workflow2"},
            ]
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        result = await service.find_workflows()

        assert len(result) == 2
        assert result[0]["name"] == "Workflow1"

    @pytest.mark.asyncio
    async def test_find_workflows_with_name_filter(self):
        """Test find_workflows filters by name."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [{"_id": "wf1", "name": "TestWorkflow"}]
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        result = await service.find_workflows(name="TestWorkflow")

        assert len(result) == 1
        assert result[0]["name"] == "TestWorkflow"

        # Verify correct params were passed
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["equals[name]"] == "TestWorkflow"

    @pytest.mark.asyncio
    async def test_find_workflows_with_include_param(self):
        """Test find_workflows includes optional fields."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [{"_id": "wf1", "name": "Workflow1", "details": {}}]
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        await service.find_workflows(include="details")

        # Verify correct params were passed
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["include"] == "details"

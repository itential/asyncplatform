# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.services.agent_projects module."""

from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asyncplatform import context
from asyncplatform.services.agent_projects import Service


class TestAgentProjectsServiceInitialization:
    """Test suite for AgentProjects Service initialization."""

    def test_service_has_name_attribute(self):
        """Test Service has name attribute set to 'agent_projects'."""
        assert hasattr(Service, "name")
        assert Service.name == "agent_projects"

    def test_service_init_with_context(self):
        """Test Service initializes with context and stores it."""
        ctx = context.Context()
        service = Service(ctx)

        assert service.ctx is ctx


class TestAgentProjectsServiceDescribeAgentProject:
    """Test suite for describe_agent_project method."""

    @pytest.mark.asyncio
    async def test_describe_agent_project_returns_data(self):
        """Test describe_agent_project returns project dict when found."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                    "_id": "project123",
                    "name": "TestProject",
                    "description": "A test project",
            }
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.describe_agent_project("project123")

        assert result is not None
        assert result["_id"] == "project123"
        assert result["name"] == "TestProject"

    @pytest.mark.asyncio
    async def test_describe_agent_project_returns_none_when_missing_data_key(self):
        """Test describe_agent_project returns None when response has no 'data' key."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {}

        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.describe_agent_project("project123")

        assert result is None


class TestAgentProjectsServiceGetAgentProjects:
    """Test suite for get_agent_projects method."""

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_get_agent_projects_returns_list(self, mock_get):
        """Test get_agent_projects returns list of projects."""
        ctx = context.Context()
        service = Service(ctx)
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "metadata": {"total": 2},
                "items": [
                    {"_id": "1", "name": "Project1"},
                    {"_id": "2", "name": "Project2"},
                ],
            }
        }
        mock_get.return_value = mock_response

        result = await service.get_agent_projects()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "Project1"
        assert result[1]["name"] == "Project2"

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_get_agent_projects_returns_empty_list_when_total_is_zero(self, mock_get):
        """Test get_agent_projects returns empty list when total is 0."""
        ctx = context.Context()
        service = Service(ctx)
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "metadata": {"total": 0},
                "items": [],
            }
        }
        mock_get.return_value = mock_response

        result = await service.get_agent_projects()
        assert result == []

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_get_agent_projects_handles_pagination(self, mock_get):
        """Test get_agent_projects returns items directly when total fits one page."""
        page1 = Mock()
        page1.json.return_value = {
            "data": {
                "metadata": {"total": 250},
                "items": [{"_id": f"{i}", "name": f"Project{i}"} for i in range(100)],
            }
        }

        page2 = Mock()
        page2.json.return_value = {
            "data": {
                "metadata": {"total": 250},
                "items": [{"_id": f"{i}", "name": f"Project{i}"} for i in range(100, 200)],
            }
        }

        page3 = Mock()
        page3.json.return_value = {
            "data": {
                "metadata": {"total": 250},
                "items": [{"_id": f"{i}", "name": f"Project{i}"} for i in range(200, 250)],
            }
        }

        mock_get.side_effect = [page1, page2, page3]

        ctx = context.Context()
        service = Service(ctx)

        result = await service.get_agent_projects()

        assert len(result) == 250
        assert result[0]["name"] == "Project0"
        assert result[249]["name"] == "Project249"

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_get_agent_projects_handles_pagination_with_exception(self, mock_get):
        """Test get_agent_projects re-raises exceptions from concurrent page requests."""
        page1 = Mock()
        page1.json.return_value = {
            "data": {
                "metadata": {"total": 250},
                "items": [{"_id": f"{i}", "name": f"Project{i}"} for i in range(100)],
            }
        }

        mock_get.side_effect = [page1, RuntimeError("API error")]

        ctx = context.Context()
        service = Service(ctx)

        with pytest.raises(RuntimeError, match="API error"):
            await service.get_agent_projects()


class TestAgentProjectsServiceDeleteAgentProject:
    """Test suite for delete_agent_project method."""

    @pytest.mark.asyncio
    async def test_delete_agent_project_returns_json_response(self):
        """Test delete_agent_project returns the parsed JSON response body."""
        ctx = context.Context()
        service = Service(ctx)
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "message": "success",
            "data": {
                "_id": "0",
                "name": "Project0",
            },
        }

        mock_client.delete = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        result = await service.delete_agent_project("0")

        assert result["message"] == "success"
        assert len(result["data"]) == 2


class TestAgentProjectsServicePatchAgentProject:
    """Test suite for patch_agent_project method."""

    @pytest.mark.asyncio
    async def test_patch_project_updates_fields(self):
        """Test patch_agent_project hits /agent-project-service/projects/{id}."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_client.patch = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        update_data = {"name": "UpdatedName", "description": "Updated description"}

        result = await service.patch_agent_project("project123", update_data)

        assert result is mock_response


class TestAgentProjectsServiceFindAgentProjects:
    """Test suite for find_agent_projects method."""

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_find_agent_projects_filters_by_name(self, mock_get):
        """Test find_agent_projects returns all items when name is not provided."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "metadata": {"total": 2},
                "items": [
                    {"_id": "1", "name": "TestProject"},
                    {"_id": "2", "name": "OtherProject"},
                ],
            }
        }
        mock_get.return_value = mock_response
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.find_agent_projects(name="TestProject")

        assert len(result) == 1
        assert result[0]["name"] == "TestProject"

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_find_agent_projects_returns_all_when_name_is_none(self, mock_get):
        """Test find_agent_projects returns only projects matching the given name."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "metadata": {"total": 2},
                "items": [
                    {"_id": "1", "name": "TestProject"},
                    {"_id": "2", "name": "OtherProject"},
                ],
            }
        }
        mock_get.return_value = mock_response
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.find_agent_projects(name=None)

        assert len(result) == 2

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_find_agent_projects_returns_empty_list_when_no_match(self, mock_get):
        """Test find_agent_projects returns empty list when name does not match any project."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "metadata": {"total": 2},
                "items": [
                    {"_id": "1", "name": "TestProject"},
                    {"_id": "2", "name": "OtherProject"},
                ],
            }
        }
        mock_get.return_value = mock_response
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.find_agent_projects(name="")

        assert len(result) == 0

    @pytest.mark.asyncio
    @patch.object(Service, "get")
    async def test_find_agent_projects_returns_empty_list_when_no_projects_exist(self, mock_get):
        """Test find_agent_projects returns empty list when there are no projects."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "metadata": {"total": 0},
                "items": [],
            }
        }
        mock_get.return_value = mock_response
        ctx.client = mock_client
        service = Service(ctx)

        result = await service.find_agent_projects(name="")

        assert result == []


class TestAgentProjectsServiceImportAgentProject:
    """Test suite for import_agent_project method."""

    @pytest.mark.asyncio
    async def test_import_agent_project_returns_project_data(self):
        """Test import_agent_project returns the imported project dict from response."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "message": "success",
            "data": {
                "_id": "new_project_123",
            }
        }

        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        project_data = {"name": "ImportedProject", "description": "Imported project", "agents": []}

        result = await service.import_agent_project(project_data)

        assert result["_id"] == "new_project_123"

    @pytest.mark.asyncio
    async def test_import_project_passes_correct_params(self):
        """Test import_project passes correct parameters to API."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "_id": "123",
                "name": "Test"
            }
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        project_data = {"name": "Test", "agents": []}

        await service.import_agent_project(project_data)

        # Verify correct endpoint and payload
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/agent-project-service/project-bundles/import"
        payload = call_args[1]["json"]
        assert payload["bundle"] == project_data
        assert payload["conflictMode"] == "replace"


    @pytest.mark.asyncio
    async def test_import_agent_project_omits_provider_resolutions_by_default(self):
        """Test import_agent_project omits providerResolutions when not specified."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "_id": "123",
                "name": "Test"
            }
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        project_data = {"name": "Test", "agents": [{"_id": "1", "name": "test",}]}

        await service.import_agent_project(project_data)

        # Verify providerResolutions is omitted so the bundle's own agent
        # provider fields are used as-is by the destination platform
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert "providerResolutions" not in payload

    @pytest.mark.asyncio
    async def test_import_agent_project_passes_through_provider_resolutions(self):
        """Test import_agent_project includes providerResolutions when explicitly given."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "_id": "123",
                "name": "Test"
            }
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        project_data = {"name": "Test", "agents": [{"_id": "1", "name": "test",}]}
        resolutions = {"1": {"profileName": "openai", "modelName": "gpt-5"}}

        await service.import_agent_project(project_data, provider_resolutions=resolutions)

        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["providerResolutions"] == resolutions


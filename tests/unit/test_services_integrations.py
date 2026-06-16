# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.services.integrations module."""

from unittest.mock import AsyncMock
from unittest.mock import Mock

import pytest

from asyncplatform import context
from asyncplatform import exceptions
from asyncplatform.services.integrations import Service

SAMPLE_PROPERTIES = {"host": "device.example.com", "port": 22}


def _make_service():
    ctx = context.Context()
    ctx.client = Mock()
    return Service(ctx)


def _mock_response(data: dict) -> Mock:
    res = Mock()
    res.json.return_value = data
    return res


class TestIntegrationsServiceInit:
    """Test suite for Service initialization."""

    def test_service_has_name_attribute(self):
        """Test Service has correct name attribute."""
        assert Service.name == "integrations"

    def test_service_init_with_context(self):
        """Test Service initializes with context."""
        ctx = context.Context()
        service = Service(ctx)
        assert service.ctx is ctx

    def test_service_has_pagination_limit(self):
        """Test Service has PAGINATION_LIMIT attribute."""
        assert Service.PAGINATION_LIMIT == 100


class TestFindIntegrations:
    """Test suite for find_integrations method."""

    @pytest.mark.asyncio
    async def test_find_returns_empty_list_when_none_exist(self):
        """Test find returns empty list when total is zero."""
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 0, "integrations": []})
        )

        result = await service.find_integrations()

        assert result == []

    @pytest.mark.asyncio
    async def test_find_returns_single_page(self):
        """Test find returns results fitting in a single page."""
        instances = [{"name": f"instance_{i}"} for i in range(3)]
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 3, "integrations": instances})
        )

        result = await service.find_integrations()

        assert len(result) == 3
        assert result[0]["name"] == "instance_0"

    @pytest.mark.asyncio
    async def test_find_paginates_across_multiple_pages(self):
        """Test find fetches all pages when total exceeds limit."""
        page1_instances = [{"name": f"instance_{i}"} for i in range(100)]
        page2_instances = [{"name": f"instance_{i}"} for i in range(100, 150)]

        page1 = _mock_response({"total": 150, "integrations": page1_instances})
        page2 = _mock_response({"total": 150, "integrations": page2_instances})

        service = _make_service()
        service.ctx.client.get = AsyncMock(side_effect=[page1, page2])

        result = await service.find_integrations()

        assert len(result) == 150
        assert service.ctx.client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_find_with_name_filter(self):
        """Test find passes name filter as query params."""
        instance = [{"name": "my-integration"}]
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 1, "integrations": instance})
        )

        result = await service.find_integrations(name="my-integration")

        assert len(result) == 1
        call_kwargs = service.ctx.client.get.call_args[1]
        assert call_kwargs["params"]["equals"] == "my-integration"

    @pytest.mark.asyncio
    async def test_find_sorts_by_name(self):
        """Test find sorts results by name for consistent pagination."""
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 0, "integrations": []})
        )

        await service.find_integrations()

        call_kwargs = service.ctx.client.get.call_args[1]
        assert call_kwargs["params"]["sort"] == "name"

    @pytest.mark.asyncio
    async def test_find_propagates_exception_from_pagination(self):
        """Test find raises AsyncPlatformError when a page request fails."""
        page1 = _mock_response({"total": 150, "integrations": [{"name": "i"}] * 100})

        service = _make_service()
        service.ctx.client.get = AsyncMock(
            side_effect=[page1, RuntimeError("Network error")]
        )

        with pytest.raises(exceptions.AsyncPlatformError):
            await service.find_integrations()


class TestCreateIntegration:
    """Test suite for create_integration method."""

    @pytest.mark.asyncio
    async def test_create_succeeds_when_no_existing_instance(self):
        """Test create succeeds when no instance with same name exists."""
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 0, "integrations": []})
        )
        service.ctx.client.post = AsyncMock(
            return_value=_mock_response({"message": "Created", "data": {"name": "my-integration"}})
        )

        result = await service.create_integration(
            name="my-integration",
            type="ssh",
            properties=SAMPLE_PROPERTIES,
        )

        assert result == {"name": "my-integration"}
        service.ctx.client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_raises_when_instance_already_exists(self):
        """Test create raises AsyncPlatformError when name already exists."""
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 1, "integrations": [{"name": "my-integration"}]})
        )

        with pytest.raises(exceptions.AsyncPlatformError, match="already exists"):
            await service.create_integration(
                name="my-integration",
                type="ssh",
                properties=SAMPLE_PROPERTIES,
            )

        service.ctx.client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_includes_optional_virtual_flag(self):
        """Test create includes virtual flag when provided."""
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 0, "integrations": []})
        )
        service.ctx.client.post = AsyncMock(
            return_value=_mock_response({"message": "Created", "data": {}})
        )

        await service.create_integration(
            name="my-integration",
            type="ssh",
            properties=SAMPLE_PROPERTIES,
            virtual=True,
        )

        call_kwargs = service.ctx.client.post.call_args[1]
        assert call_kwargs["json"]["virtual"] is True

    @pytest.mark.asyncio
    async def test_create_includes_optional_model(self):
        """Test create includes model when provided."""
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 0, "integrations": []})
        )
        service.ctx.client.post = AsyncMock(
            return_value=_mock_response({"message": "Created", "data": {}})
        )

        await service.create_integration(
            name="my-integration",
            type="ssh",
            properties=SAMPLE_PROPERTIES,
            model="My API:1.0.0",
        )

        call_kwargs = service.ctx.client.post.call_args[1]
        assert call_kwargs["json"]["model"] == "My API:1.0.0"

    @pytest.mark.asyncio
    async def test_create_omits_none_optional_fields(self):
        """Test create omits virtual and model when not provided."""
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 0, "integrations": []})
        )
        service.ctx.client.post = AsyncMock(
            return_value=_mock_response({"message": "Created", "data": {}})
        )

        await service.create_integration(
            name="my-integration",
            type="ssh",
            properties=SAMPLE_PROPERTIES,
        )

        call_kwargs = service.ctx.client.post.call_args[1]
        assert "virtual" not in call_kwargs["json"]
        assert "model" not in call_kwargs["json"]


class TestGetIntegration:
    """Test suite for get_integration method."""

    @pytest.mark.asyncio
    async def test_get_returns_integration_data(self):
        """Test get returns integration instance data."""
        expected = {"metadata": {"isActive": True}, "data": {"type": "ssh"}}
        service = _make_service()
        service.ctx.client.get = AsyncMock(return_value=_mock_response(expected))

        result = await service.get_integration("my-integration")

        assert result == expected

    @pytest.mark.asyncio
    async def test_get_calls_correct_endpoint(self):
        """Test get calls the correct endpoint path."""
        service = _make_service()
        service.ctx.client.get = AsyncMock(return_value=_mock_response({}))

        await service.get_integration("my-integration")

        call_args = service.ctx.client.get.call_args
        assert "/integrations/my-integration" in call_args[0][0]


class TestDeleteIntegration:
    """Test suite for delete_integration method."""

    @pytest.mark.asyncio
    async def test_delete_returns_response_data(self):
        """Test delete returns the response body."""
        expected = {"message": "Deleted", "name": "my-integration"}
        service = _make_service()
        service.ctx.client.delete = AsyncMock(return_value=_mock_response(expected))

        result = await service.delete_integration("my-integration")

        assert result == expected

    @pytest.mark.asyncio
    async def test_delete_calls_correct_endpoint(self):
        """Test delete calls the correct endpoint path."""
        service = _make_service()
        service.ctx.client.delete = AsyncMock(return_value=_mock_response({}))

        await service.delete_integration("my-integration")

        call_args = service.ctx.client.delete.call_args
        assert "/integrations/my-integration" in call_args[0][0]

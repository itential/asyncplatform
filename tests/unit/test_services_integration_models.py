# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.services.integration_models module."""

from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asyncplatform import context
from asyncplatform import exceptions
from asyncplatform.services.integration_models import Service

SAMPLE_SPEC = {
    "info": {"title": "My API", "version": "1.0.0"},
    "openapi": "3.0.0",
    "paths": {},
}

VERSION_ID = "My API:1.0.0"


def _make_service():
    ctx = context.Context()
    ctx.client = Mock()
    return Service(ctx)


def _mock_response(data: dict) -> Mock:
    res = Mock()
    res.json.return_value = data
    return res


class TestIntegrationModelsServiceInit:
    """Test suite for Service initialization."""

    def test_service_has_name_attribute(self):
        """Test Service has correct name attribute."""
        assert Service.name == "integration_models"

    def test_service_init_with_context(self):
        """Test Service initializes with context."""
        ctx = context.Context()
        service = Service(ctx)
        assert service.ctx is ctx

    def test_service_has_pagination_limit(self):
        """Test Service has PAGINATION_LIMIT attribute."""
        assert Service.PAGINATION_LIMIT == 100


class TestFindIntegrationModels:
    """Test suite for find_integration_models method."""

    @pytest.mark.asyncio
    async def test_find_returns_empty_list_when_none_exist(self):
        """Test find returns empty list when total is zero."""
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 0, "integrationModels": []})
        )

        result = await service.find_integration_models()

        assert result == []

    @pytest.mark.asyncio
    async def test_find_returns_single_page(self):
        """Test find returns results fitting in a single page."""
        models = [{"name": f"model_{i}"} for i in range(3)]
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 3, "integrationModels": models})
        )

        result = await service.find_integration_models()

        assert len(result) == 3
        assert result[0]["name"] == "model_0"

    @pytest.mark.asyncio
    async def test_find_paginates_across_multiple_pages(self):
        """Test find fetches all pages when total exceeds limit."""
        page1_models = [{"name": f"model_{i}"} for i in range(100)]
        page2_models = [{"name": f"model_{i}"} for i in range(100, 150)]

        page1 = _mock_response({"total": 150, "integrationModels": page1_models})
        page2 = _mock_response({"total": 150, "integrationModels": page2_models})

        service = _make_service()
        service.ctx.client.get = AsyncMock(side_effect=[page1, page2])

        result = await service.find_integration_models()

        assert len(result) == 150
        assert service.ctx.client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_find_with_name_filter(self):
        """Test find passes name filter as query params."""
        model = [{"name": VERSION_ID}]
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 1, "integrationModels": model})
        )

        result = await service.find_integration_models(name=VERSION_ID)

        assert len(result) == 1
        call_kwargs = service.ctx.client.get.call_args[1]
        assert call_kwargs["params"]["equals"] == VERSION_ID

    @pytest.mark.asyncio
    async def test_find_propagates_exception_from_pagination(self):
        """Test find raises AsyncPlatformError when a page request fails."""
        page1 = _mock_response({"total": 150, "integrationModels": [{"name": "m"}] * 100})

        service = _make_service()
        service.ctx.client.get = AsyncMock(
            side_effect=[page1, RuntimeError("Network error")]
        )

        with pytest.raises(exceptions.AsyncPlatformError):
            await service.find_integration_models()


class TestCreateIntegrationModel:
    """Test suite for create_integration_model method."""

    @pytest.mark.asyncio
    async def test_create_succeeds_when_no_existing_model(self):
        """Test create succeeds when no model with same version_id exists."""
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 0, "integrationModels": []})
        )
        service.ctx.client.post = AsyncMock(
            return_value=_mock_response({"message": "Created", "data": {"name": VERSION_ID}})
        )

        result = await service.create_integration_model(SAMPLE_SPEC)

        assert result == {"name": VERSION_ID}
        service.ctx.client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_raises_when_model_already_exists(self):
        """Test create raises AsyncPlatformError when version_id already exists."""
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 1, "integrationModels": [{"name": VERSION_ID}]})
        )

        with pytest.raises(exceptions.AsyncPlatformError, match="already exists"):
            await service.create_integration_model(SAMPLE_SPEC)

        service.ctx.client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_raises_when_spec_too_large(self):
        """Test create raises AsyncPlatformError when spec exceeds 15 MB."""
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 0, "integrationModels": []})
        )

        with patch("json.dumps", return_value="x" * (15 * 1024 * 1024 + 1)):
            with pytest.raises(exceptions.AsyncPlatformError, match="exceeds"):
                await service.create_integration_model(SAMPLE_SPEC)

        service.ctx.client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_posts_spec_wrapped_in_model_key(self):
        """Test create sends spec under the 'model' key in the request body."""
        service = _make_service()
        service.ctx.client.get = AsyncMock(
            return_value=_mock_response({"total": 0, "integrationModels": []})
        )
        service.ctx.client.post = AsyncMock(
            return_value=_mock_response({"message": "Created", "data": {}})
        )

        await service.create_integration_model(SAMPLE_SPEC)

        call_kwargs = service.ctx.client.post.call_args[1]
        assert call_kwargs["json"]["model"] == SAMPLE_SPEC


class TestGetIntegrationModel:
    """Test suite for get_integration_model method."""

    @pytest.mark.asyncio
    async def test_get_returns_model_data(self):
        """Test get returns integration model data."""
        expected = {"name": VERSION_ID, "model": {}}
        service = _make_service()
        service.ctx.client.get = AsyncMock(return_value=_mock_response(expected))

        result = await service.get_integration_model(VERSION_ID)

        assert result == expected

    @pytest.mark.asyncio
    async def test_get_calls_correct_endpoint(self):
        """Test get calls the correct endpoint path."""
        service = _make_service()
        service.ctx.client.get = AsyncMock(return_value=_mock_response({}))

        await service.get_integration_model(VERSION_ID)

        call_args = service.ctx.client.get.call_args
        assert f"/integration-models/{VERSION_ID}" in call_args[0][0]


class TestUpdateIntegrationModel:
    """Test suite for update_integration_model method."""

    @pytest.mark.asyncio
    async def test_update_succeeds(self):
        """Test update sends spec and returns updated model data."""
        service = _make_service()
        service.ctx.client.put = AsyncMock(
            return_value=_mock_response({"message": "Updated", "data": {"name": VERSION_ID}})
        )

        result = await service.update_integration_model(SAMPLE_SPEC)

        assert result == {"name": VERSION_ID}
        service.ctx.client.put.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_raises_when_spec_too_large(self):
        """Test update raises AsyncPlatformError when spec exceeds 15 MB."""
        service = _make_service()

        with patch("json.dumps", return_value="x" * (15 * 1024 * 1024 + 1)):
            with pytest.raises(exceptions.AsyncPlatformError, match="exceeds"):
                await service.update_integration_model(SAMPLE_SPEC)

        service.ctx.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_puts_spec_wrapped_in_model_key(self):
        """Test update sends spec under the 'model' key."""
        service = _make_service()
        service.ctx.client.put = AsyncMock(
            return_value=_mock_response({"message": "Updated", "data": {}})
        )

        await service.update_integration_model(SAMPLE_SPEC)

        call_kwargs = service.ctx.client.put.call_args[1]
        assert call_kwargs["json"]["model"] == SAMPLE_SPEC


class TestDeleteIntegrationModel:
    """Test suite for delete_integration_model method."""

    @pytest.mark.asyncio
    async def test_delete_returns_response_data(self):
        """Test delete returns the response body."""
        expected = {"message": "Deleted", "name": VERSION_ID}
        service = _make_service()
        service.ctx.client.delete = AsyncMock(return_value=_mock_response(expected))

        result = await service.delete_integration_model(VERSION_ID)

        assert result == expected

    @pytest.mark.asyncio
    async def test_delete_calls_correct_endpoint(self):
        """Test delete calls the correct endpoint path."""
        service = _make_service()
        service.ctx.client.delete = AsyncMock(return_value=_mock_response({}))

        await service.delete_integration_model(VERSION_ID)

        call_args = service.ctx.client.delete.call_args
        assert f"/integration-models/{VERSION_ID}" in call_args[0][0]

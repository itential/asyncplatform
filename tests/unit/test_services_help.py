# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.services.help module."""

from unittest.mock import AsyncMock
from unittest.mock import Mock

import pytest

from asyncplatform import context
from asyncplatform.services.help import Service


class TestHelpServiceInitialization:
    """Test suite for Help Service initialization."""

    def test_service_has_name_attribute(self):
        """Test Service has name attribute."""
        assert hasattr(Service, "name")
        assert Service.name == "help"

    def test_service_init_with_context(self):
        """Test Service initialization with context."""
        ctx = context.Context()
        service = Service(ctx)

        assert service.ctx is ctx


class TestHelpGetOpenapi:
    """Test suite for get_openapi method."""

    @pytest.mark.asyncio
    async def test_get_openapi_returns_openapi_spec(self):
        """Test get_openapi returns OpenAPI specification."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Itential Platform API", "version": "1.0.0"},
            "paths": {"/test": {"get": {"summary": "Test endpoint"}}},
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        result = await service.get_openapi()

        assert result["openapi"] == "3.0.0"
        assert result["info"]["title"] == "Itential Platform API"
        assert "/test" in result["paths"]

        # Verify default url parameter
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["url"] == "/"

    @pytest.mark.asyncio
    async def test_get_openapi_with_custom_url(self):
        """Test get_openapi with custom URL parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Custom API", "version": "1.0.0"},
            "paths": {},
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        result = await service.get_openapi(url="/custom-path")

        assert result["openapi"] == "3.0.0"
        assert result["info"]["title"] == "Custom API"

        # Verify custom url parameter was passed
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["url"] == "/custom-path"

    @pytest.mark.asyncio
    async def test_get_openapi_with_none_url(self):
        """Test get_openapi with None URL defaults to root."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "API", "version": "1.0.0"},
            "paths": {},
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        await service.get_openapi(url=None)

        # Verify None url defaults to "/"
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["url"] == "/"

    @pytest.mark.asyncio
    async def test_get_openapi_calls_correct_endpoint(self):
        """Test get_openapi calls the correct API endpoint."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"openapi": "3.0.0"}
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        await service.get_openapi()

        # Verify endpoint path
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "/help/openapi"

    @pytest.mark.asyncio
    async def test_get_openapi_returns_dict(self):
        """Test get_openapi returns a dictionary."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"openapi": "3.0.0", "paths": {}}
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)
        result = await service.get_openapi()

        assert isinstance(result, dict)
        assert "openapi" in result

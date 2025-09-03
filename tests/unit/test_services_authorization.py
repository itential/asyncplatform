# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.services.authorization module."""

from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asyncplatform import context
from asyncplatform import exceptions
from asyncplatform.services.authorization import Service


class TestAuthorizationServiceInitialization:
    """Test suite for Authorization Service initialization."""

    def test_service_has_name_attribute(self):
        """Test Service has name attribute."""
        assert hasattr(Service, "name")
        assert Service.name == "authorization"

    def test_service_init_with_context(self):
        """Test Service initialization with context."""
        ctx = context.Context()
        service = Service(ctx)

        assert service.ctx is ctx


class TestAuthorizationServiceGetAccounts:
    """Test suite for Authorization Service get_accounts method."""

    @pytest.mark.asyncio
    @patch.object(Service, "_get")
    async def test_get_accounts_returns_list(self, mock_get):
        """Test get_accounts returns list of accounts."""
        mock_get.return_value = [
            {"_id": "1", "name": "user1"},
            {"_id": "2", "name": "user2"},
        ]

        ctx = context.Context()
        service = Service(ctx)

        result = await service.get_accounts()

        assert isinstance(result, list)
        assert len(result) == 2

    @pytest.mark.asyncio
    @patch.object(Service, "_get")
    async def test_get_accounts_passes_correct_params(self, mock_get):
        """Test get_accounts passes correct parameters."""
        mock_get.return_value = []

        ctx = context.Context()
        service = Service(ctx)

        await service.get_accounts()

        # Verify _get was called with correct endpoint and params
        mock_get.assert_called_once()
        # Get the call arguments - can be positional or keyword
        args, kwargs = mock_get.call_args
        if args:
            endpoint = args[0]
            params = args[1] if len(args) > 1 else kwargs.get("params", {})
        else:
            endpoint = kwargs.get("path") or kwargs.get("endpoint")
            params = kwargs.get("params", {})

        assert endpoint == "/authorization/accounts"
        assert params["inactive"] is False
        assert params["isServiceAccount"] is False

    @pytest.mark.asyncio
    @patch.object(Service, "_get")
    async def test_get_accounts_returns_empty_list_when_no_accounts(self, mock_get):
        """Test get_accounts returns empty list when no accounts exist."""
        mock_get.return_value = []

        ctx = context.Context()
        service = Service(ctx)

        result = await service.get_accounts()

        assert isinstance(result, list)
        assert len(result) == 0


class TestAuthorizationServiceGetGroups:
    """Test suite for Authorization Service get_groups method."""

    @pytest.mark.asyncio
    @patch.object(Service, "_get")
    async def test_get_groups_returns_list(self, mock_get):
        """Test get_groups returns list of groups."""
        mock_get.return_value = [
            {"_id": "1", "name": "admin_group"},
            {"_id": "2", "name": "users_group"},
        ]

        ctx = context.Context()
        service = Service(ctx)

        result = await service.get_groups()

        assert isinstance(result, list)
        assert len(result) == 2

    @pytest.mark.asyncio
    @patch.object(Service, "_get")
    async def test_get_groups_passes_correct_params(self, mock_get):
        """Test get_groups passes correct parameters."""
        mock_get.return_value = []

        ctx = context.Context()
        service = Service(ctx)

        await service.get_groups()

        # Verify _get was called with correct endpoint and params
        mock_get.assert_called_once()
        # Get the call arguments - can be positional or keyword
        args, kwargs = mock_get.call_args
        if args:
            endpoint = args[0]
            params = args[1] if len(args) > 1 else kwargs.get("params", {})
        else:
            endpoint = kwargs.get("path") or kwargs.get("endpoint")
            params = kwargs.get("params", {})

        assert endpoint == "/authorization/groups"
        assert params["inactive"] is False

    @pytest.mark.asyncio
    @patch.object(Service, "_get")
    async def test_get_groups_returns_empty_list_when_no_groups(self, mock_get):
        """Test get_groups returns empty list when no groups exist."""
        mock_get.return_value = []

        ctx = context.Context()
        service = Service(ctx)

        result = await service.get_groups()

        assert isinstance(result, list)
        assert len(result) == 0


class TestAuthorizationServicePrivateGet:
    """Test suite for Authorization Service _get helper method."""

    @pytest.mark.asyncio
    async def test_get_with_single_page_results(self):
        """Test _get with results fitting in single page."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "total": 2,
            "results": [{"_id": "1"}, {"_id": "2"}],
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service._get("/test", {}, limit=100)

        assert len(result) == 2
        assert result[0]["_id"] == "1"
        assert result[1]["_id"] == "2"

    @pytest.mark.asyncio
    async def test_get_with_empty_results(self):
        """Test _get with zero results."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"total": 0, "results": []}
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service._get("/test", {}, limit=100)

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_with_multiple_pages(self):
        """Test _get with results spanning multiple pages."""
        ctx = context.Context()
        mock_client = Mock()

        # First response (page 1)
        mock_response1 = Mock()
        mock_response1.json.return_value = {
            "total": 250,
            "results": [{"_id": f"{i}"} for i in range(100)],
        }

        # Second response (page 2)
        mock_response2 = Mock()
        mock_response2.json.return_value = {
            "total": 250,
            "results": [{"_id": f"{i}"} for i in range(100, 200)],
        }

        # Third response (page 3)
        mock_response3 = Mock()
        mock_response3.json.return_value = {
            "total": 250,
            "results": [{"_id": f"{i}"} for i in range(200, 250)],
        }

        mock_client.get = AsyncMock(
            side_effect=[mock_response1, mock_response2, mock_response3]
        )
        ctx.client = mock_client

        service = Service(ctx)

        result = await service._get("/test", {}, limit=100)

        assert len(result) == 250
        # Verify first page
        assert result[0]["_id"] == "0"
        # Verify second page
        assert result[100]["_id"] == "100"
        # Verify third page
        assert result[200]["_id"] == "200"

    @pytest.mark.asyncio
    async def test_get_sets_pagination_params(self):
        """Test _get sets correct pagination parameters."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"total": 10, "results": [{"_id": "1"}]}
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        params = {"inactive": False}
        await service._get("/test", params, limit=50)

        # Check that pagination params were added
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["skip"] == 0
        assert call_args[1]["params"]["limit"] == 50

    @pytest.mark.asyncio
    async def test_get_uses_custom_limit(self):
        """Test _get uses custom limit parameter."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"total": 5, "results": [{"_id": "1"}]}
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        await service._get("/test", {}, limit=25)

        # Verify custom limit was used
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["limit"] == 25

    @pytest.mark.asyncio
    async def test_get_preserves_original_params(self):
        """Test _get preserves original params dict."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"total": 5, "results": [{"_id": "1"}]}
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        params = {"inactive": False, "custom": "value"}
        await service._get("/test", params, limit=25)

        # Verify custom params were preserved
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["inactive"] is False
        assert call_args[1]["params"]["custom"] == "value"


class TestAuthorizationServiceIntegration:
    """Integration tests for Authorization Service."""

    @pytest.mark.asyncio
    @patch.object(Service, "_get")
    async def test_get_accounts_integration(self, mock_get):
        """Test get_accounts complete workflow."""
        mock_get.return_value = [
            {"_id": "1", "name": "admin", "email": "admin@example.com"},
            {"_id": "2", "name": "user1", "email": "user1@example.com"},
            {"_id": "3", "name": "user2", "email": "user2@example.com"},
        ]

        ctx = context.Context()
        service = Service(ctx)

        result = await service.get_accounts()

        assert len(result) == 3
        assert result[0]["name"] == "admin"
        assert result[1]["email"] == "user1@example.com"

    @pytest.mark.asyncio
    @patch.object(Service, "_get")
    async def test_get_groups_integration(self, mock_get):
        """Test get_groups complete workflow."""
        mock_get.return_value = [
            {"_id": "1", "name": "admins", "description": "Admin group"},
            {"_id": "2", "name": "users", "description": "User group"},
        ]

        ctx = context.Context()
        service = Service(ctx)

        result = await service.get_groups()

        assert len(result) == 2
        assert result[0]["name"] == "admins"
        assert result[1]["description"] == "User group"

    @pytest.mark.asyncio
    async def test_service_handles_large_dataset(self):
        """Test service handles paginated large datasets correctly."""
        ctx = context.Context()
        mock_client = Mock()

        # Simulate 350 total items across 4 pages
        page1_response = Mock()
        page1_response.json.return_value = {
            "total": 350,
            "results": [{"_id": f"id_{i}"} for i in range(100)],
        }

        page2_response = Mock()
        page2_response.json.return_value = {
            "total": 350,
            "results": [{"_id": f"id_{i}"} for i in range(100, 200)],
        }

        page3_response = Mock()
        page3_response.json.return_value = {
            "total": 350,
            "results": [{"_id": f"id_{i}"} for i in range(200, 300)],
        }

        page4_response = Mock()
        page4_response.json.return_value = {
            "total": 350,
            "results": [{"_id": f"id_{i}"} for i in range(300, 350)],
        }

        mock_client.get = AsyncMock(
            side_effect=[page1_response, page2_response, page3_response, page4_response]
        )
        ctx.client = mock_client

        service = Service(ctx)

        result = await service.get_accounts()

        # Should have fetched all 350 items
        assert len(result) == 350
        assert result[0]["_id"] == "id_0"
        assert result[349]["_id"] == "id_349"

        # Should have made 4 requests (1 initial + 3 concurrent)
        assert mock_client.get.call_count == 4

    @pytest.mark.asyncio
    async def test_service_concurrent_pagination(self):
        """Test service properly handles concurrent page requests."""
        ctx = context.Context()
        mock_client = Mock()

        # First page shows we need 3 pages total
        page1 = Mock()
        page1.json.return_value = {
            "total": 250,
            "results": [{"_id": f"id_{i}"} for i in range(100)],
        }

        page2 = Mock()
        page2.json.return_value = {
            "total": 250,
            "results": [{"_id": f"id_{i}"} for i in range(100, 200)],
        }

        page3 = Mock()
        page3.json.return_value = {
            "total": 250,
            "results": [{"_id": f"id_{i}"} for i in range(200, 250)],
        }

        mock_client.get = AsyncMock(side_effect=[page1, page2, page3])
        ctx.client = mock_client

        service = Service(ctx)
        result = await service.get_groups()

        # Verify all pages were fetched
        assert len(result) == 250
        # Verify concurrent requests were made (3 total calls)
        assert mock_client.get.call_count == 3

    @pytest.mark.asyncio
    async def test_get_propagates_exception_from_pagination(self):
        """Test _get properly propagates exceptions from concurrent requests."""
        ctx = context.Context()
        mock_client = Mock()

        # First page succeeds
        page1 = Mock()
        page1.json.return_value = {
            "total": 250,
            "results": [{"_id": f"id_{i}"} for i in range(100)],
        }

        # Second page raises exception
        mock_client.get = AsyncMock(side_effect=[page1, RuntimeError("Network error")])
        ctx.client = mock_client

        service = Service(ctx)

        # ServiceBase wraps exceptions in AsyncPlatformError
        with pytest.raises(exceptions.AsyncPlatformError, match="Network error"):
            await service._get("/test", {}, limit=100)

    @pytest.mark.asyncio
    async def test_get_limit_exactly_equals_total(self):
        """Test _get when total exactly equals limit (no pagination needed)."""
        ctx = context.Context()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "total": 100,
            "results": [{"_id": f"id_{i}"} for i in range(100)],
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = Service(ctx)

        result = await service._get("/test", {}, limit=100)

        # Should make only one request (no pagination)
        assert mock_client.get.call_count == 1
        assert len(result) == 100
        assert result[0]["_id"] == "id_0"
        assert result[99]["_id"] == "id_99"

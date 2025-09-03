# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.services.ServiceBase class."""

from unittest.mock import AsyncMock
from unittest.mock import Mock

import pytest

from asyncplatform import context
from asyncplatform.http import HTTPMethod
from asyncplatform.http import HTTPStatus
from asyncplatform.services import ServiceBase


class TestServiceBaseInitialization:
    """Test suite for ServiceBase initialization."""

    def test_service_base_init_with_context(self):
        """Test ServiceBase initialization with context.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        service = ServiceBase(ctx)

        assert service.ctx is ctx

    def test_service_base_stores_context_reference(self):
        """Test ServiceBase stores context reference.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        ctx.client = Mock()
        service = ServiceBase(ctx)

        assert service.ctx.client is ctx.client


class TestServiceBaseSendRequest:
    """Test suite for ServiceBase._send_request method."""

    @pytest.mark.asyncio
    async def test_send_request_get_method(self):
        """Test _send_request with GET method.

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
        mock_response.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        result = await service._send_request(HTTPMethod.GET, "/test")

        assert result is mock_response
        mock_client.get.assert_called_once_with("/test")

    @pytest.mark.asyncio
    async def test_send_request_post_method_with_json(self):
        """Test _send_request with POST method and JSON body.

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
        mock_response.status_code = 201
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        json_data = {"key": "value"}
        result = await service._send_request(
            HTTPMethod.POST, "/test", json=json_data
        )

        assert result is mock_response
        mock_client.post.assert_called_once_with("/test", json=json_data)

    @pytest.mark.asyncio
    async def test_send_request_with_params(self):
        """Test _send_request with query parameters.

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
        mock_response.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        params = {"limit": 10, "offset": 20}
        result = await service._send_request(
            HTTPMethod.GET, "/test", params=params
        )

        assert result is mock_response
        mock_client.get.assert_called_once_with("/test", params=params)

    @pytest.mark.asyncio
    async def test_send_request_validates_expected_status(self):
        """Test _send_request validates expected status code.

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
        mock_response.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        # Should not raise when status matches
        result = await service._send_request(
            HTTPMethod.GET, "/test", expected_status=HTTPStatus.OK
        )

        assert result is mock_response

    @pytest.mark.asyncio
    async def test_send_request_logs_warning_on_status_mismatch(self):
        """Test _send_request returns response even when status doesn't match expected.

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
        mock_response.status_code = 404
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        # Should not raise exception even when status doesn't match
        result = await service._send_request(
            HTTPMethod.GET, "/test", expected_status=HTTPStatus.OK
        )

        # Should still return the response despite status mismatch
        assert result is mock_response
        assert result.status_code == 404



class TestServiceBaseGetMethod:
    """Test suite for ServiceBase.get convenience method."""

    @pytest.mark.asyncio
    async def test_get_calls_send_request_with_get_method(self):
        """Test get() calls _send_request with GET method.

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
        mock_response.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        result = await service.get("/test")

        assert result is mock_response
        mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_passes_params(self):
        """Test get() passes params to _send_request.

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
        mock_response.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        params = {"limit": 10}
        await service.get("/test", params=params)

        mock_client.get.assert_called_once_with("/test", params=params)

    @pytest.mark.asyncio
    async def test_get_defaults_to_ok_status(self):
        """Test get() defaults expected_status to OK.

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
        mock_response.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        # Should not raise with 200 status
        result = await service.get("/test")
        assert result is mock_response


class TestServiceBasePostMethod:
    """Test suite for ServiceBase.post convenience method."""

    @pytest.mark.asyncio
    async def test_post_calls_send_request_with_post_method(self):
        """Test post() calls _send_request with POST method.

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
        mock_response.status_code = 201
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        result = await service.post("/test", json={"key": "value"})

        assert result is mock_response
        mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_defaults_to_created_status(self):
        """Test post() defaults expected_status to CREATED.

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
        mock_response.status_code = 201
        mock_client.post = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        # Should not log warning with 201 status
        result = await service.post("/test")
        assert result is mock_response


class TestServiceBasePutMethod:
    """Test suite for ServiceBase.put convenience method."""

    @pytest.mark.asyncio
    async def test_put_calls_send_request_with_put_method(self):
        """Test put() calls _send_request with PUT method.

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
        mock_response.status_code = 200
        mock_client.put = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        result = await service.put("/test", json={"key": "value"})

        assert result is mock_response
        mock_client.put.assert_called_once()

    @pytest.mark.asyncio
    async def test_put_defaults_to_ok_status(self):
        """Test put() defaults expected_status to OK.

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
        mock_response.status_code = 200
        mock_client.put = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        result = await service.put("/test")
        assert result is mock_response


class TestServiceBasePatchMethod:
    """Test suite for ServiceBase.patch convenience method."""

    @pytest.mark.asyncio
    async def test_patch_calls_send_request_with_patch_method(self):
        """Test patch() calls _send_request with PATCH method.

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
        mock_response.status_code = 200
        mock_client.patch = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        result = await service.patch("/test", json={"key": "value"})

        assert result is mock_response
        mock_client.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_patch_defaults_to_ok_status(self):
        """Test patch() defaults expected_status to OK.

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
        mock_response.status_code = 200
        mock_client.patch = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        result = await service.patch("/test")
        assert result is mock_response


class TestServiceBaseDeleteMethod:
    """Test suite for ServiceBase.delete convenience method."""

    @pytest.mark.asyncio
    async def test_delete_calls_send_request_with_delete_method(self):
        """Test delete() calls _send_request with DELETE method.

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
        mock_response.status_code = 204
        mock_client.delete = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        result = await service.delete("/test")

        assert result is mock_response
        mock_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_defaults_to_no_content_status(self):
        """Test delete() defaults expected_status to NO_CONTENT.

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
        mock_response.status_code = 204
        mock_client.delete = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        result = await service.delete("/test")
        assert result is mock_response


class TestServiceBaseExceptionHandling:
    """Test suite for ServiceBase exception handling."""

    @pytest.mark.asyncio
    async def test_send_request_handles_request_error(self):
        """Test _send_request converts RequestError to AsyncPlatformError.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import httpx
        import ipsdk.exceptions

        ctx = context.Context()
        mock_client = Mock()
        # Create a proper httpx RequestError
        http_error = httpx.RequestError("Connection failed")
        mock_client.get = AsyncMock(
            side_effect=ipsdk.exceptions.RequestError(http_error)
        )
        ctx.client = mock_client

        service = ServiceBase(ctx)

        with pytest.raises(Exception) as exc_info:
            await service._send_request(HTTPMethod.GET, "/test")

        assert "Request error" in str(exc_info.value)
        assert "/test" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_request_handles_http_connect_error(self):
        """Test _send_request handles httpx ConnectError via generic handler.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import httpx

        ctx = context.Context()
        mock_client = Mock()
        mock_client.get = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        ctx.client = mock_client

        service = ServiceBase(ctx)

        with pytest.raises(Exception) as exc_info:
            await service._send_request(HTTPMethod.GET, "/test")

        # Will be caught by generic exception handler
        assert "Unexpected error during GET /test" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_request_handles_http_timeout(self):
        """Test _send_request handles httpx timeout via generic handler.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import httpx

        ctx = context.Context()
        mock_client = Mock()
        mock_client.get = AsyncMock(
            side_effect=httpx.TimeoutException("Request timed out")
        )
        ctx.client = mock_client

        service = ServiceBase(ctx)

        with pytest.raises(Exception) as exc_info:
            await service._send_request(HTTPMethod.GET, "/test")

        # Will be caught by generic exception handler
        assert "Unexpected error during GET /test" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_request_handles_unexpected_exception(self):
        """Test _send_request handles unexpected exceptions.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = Mock()
        mock_client.get = AsyncMock(side_effect=ValueError("Unexpected error"))
        ctx.client = mock_client

        service = ServiceBase(ctx)

        with pytest.raises(Exception) as exc_info:
            await service._send_request(HTTPMethod.GET, "/test")

        assert "Unexpected error during GET /test" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_propagates_httpx_connect_error(self):
        """Test get() propagates httpx connection errors.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import httpx

        ctx = context.Context()
        mock_client = Mock()
        mock_client.get = AsyncMock(
            side_effect=httpx.ConnectError("Network error")
        )
        ctx.client = mock_client

        service = ServiceBase(ctx)

        with pytest.raises(Exception) as exc_info:
            await service.get("/test")

        assert "Unexpected error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_post_propagates_httpx_timeout(self):
        """Test post() propagates httpx timeout errors.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import httpx

        ctx = context.Context()
        mock_client = Mock()
        mock_client.post = AsyncMock(
            side_effect=httpx.TimeoutException("Timeout")
        )
        ctx.client = mock_client

        service = ServiceBase(ctx)

        with pytest.raises(Exception) as exc_info:
            await service.post("/test", json={"key": "value"})

        assert "Unexpected error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_put_propagates_request_error(self):
        """Test put() propagates ipsdk RequestError.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import httpx
        import ipsdk.exceptions

        ctx = context.Context()
        mock_client = Mock()
        http_error = httpx.RequestError("500 Server Error")
        mock_client.put = AsyncMock(
            side_effect=ipsdk.exceptions.RequestError(http_error)
        )
        ctx.client = mock_client

        service = ServiceBase(ctx)

        with pytest.raises(Exception) as exc_info:
            await service.put("/test", json={"key": "value"})

        assert "Request error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_patch_propagates_exception(self):
        """Test patch() propagates exceptions.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = Mock()
        mock_client.patch = AsyncMock(side_effect=RuntimeError("Patch failed"))
        ctx.client = mock_client

        service = ServiceBase(ctx)

        with pytest.raises(Exception) as exc_info:
            await service.patch("/test", json={"key": "value"})

        assert "Unexpected error during PATCH /test" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_propagates_exception(self):
        """Test delete() propagates exceptions.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = Mock()
        mock_client.delete = AsyncMock(side_effect=RuntimeError("Delete failed"))
        ctx.client = mock_client

        service = ServiceBase(ctx)

        with pytest.raises(Exception) as exc_info:
            await service.delete("/test")

        assert "Unexpected error during DELETE /test" in str(exc_info.value)


class TestServiceBaseIntegration:
    """Integration tests for ServiceBase class."""

    @pytest.mark.asyncio
    async def test_service_base_complete_request_workflow(self):
        """Test complete request workflow through ServiceBase.

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
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"result": "success"})
        mock_client.get = AsyncMock(return_value=mock_response)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        result = await service.get("/api/endpoint", params={"id": "123"})

        assert result is mock_response
        assert result.json() == {"result": "success"}

    @pytest.mark.asyncio
    async def test_service_base_handles_multiple_requests(self):
        """Test ServiceBase handles multiple sequential requests.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = Mock()

        mock_response1 = Mock(status_code=200)
        mock_response2 = Mock(status_code=201)

        mock_client.get = AsyncMock(return_value=mock_response1)
        mock_client.post = AsyncMock(return_value=mock_response2)
        ctx.client = mock_client

        service = ServiceBase(ctx)

        result1 = await service.get("/test")
        result2 = await service.post("/test", json={"data": "value"})

        assert result1 is mock_response1
        assert result2 is mock_response2
        mock_client.get.assert_called_once()
        mock_client.post.assert_called_once()

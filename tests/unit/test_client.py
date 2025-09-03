# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.client module."""

from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asyncplatform import exceptions
from asyncplatform.client import Client


class TestClientInitialization:
    """Test suite for Client initialization."""

    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.services_loader.get")
    def test_client_initialization_with_defaults(
        self, mock_service_loader, mock_factory
    ):
        """Test Client initialization with default parameters.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_factory.return_value = Mock()
        mock_service_loader.return_value = Mock()

        c = Client()

        assert c._context is not None
        mock_factory.assert_called_once_with(want_async=True)

    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.services_loader.get")
    def test_client_initialization_with_all_parameters(
        self, mock_service_loader, mock_factory
    ):
        """Test Client initialization with all parameters.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_factory.return_value = Mock()
        mock_service_loader.return_value = Mock()

        c = Client(
            host="platform.example.com",
            port=443,
            use_tls=True,
            verify=True,
            user="admin@domain",
            password="secret",
            client_id="test_client",
            client_secret="test_secret",
            timeout=60,
        )

        assert c._context is not None
        mock_factory.assert_called_once_with(
            want_async=True,
            host="platform.example.com",
            port=443,
            use_tls=True,
            verify=True,
            user="admin@domain",
            password="secret",
            client_id="test_client",
            client_secret="test_secret",
            timeout=60,
        )

    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.services_loader.get")
    def test_client_initialization_filters_none_values(
        self, mock_service_loader, mock_factory
    ):
        """Test Client initialization filters out None values.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_factory.return_value = Mock()
        mock_service_loader.return_value = Mock()

        c = Client(host="platform.example.com", port=None, user=None)

        assert c._context is not None
        # Should only pass host and want_async
        mock_factory.assert_called_once_with(
            want_async=True, host="platform.example.com"
        )

    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.services_loader.get")
    def test_client_initialization_creates_context(
        self, mock_service_loader, mock_factory
    ):
        """Test Client initialization creates a context with client.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_service_loader.return_value = Mock()
        mock_ipsdk_client = Mock()
        mock_factory.return_value = mock_ipsdk_client

        c = Client()

        assert c._context is not None
        assert c._context.client is mock_ipsdk_client


class TestClientContextManager:
    """Test suite for Client async context manager."""

    @pytest.mark.asyncio
    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.services_loader.get")
    async def test_client_aenter_returns_self(self, mock_service_loader, mock_factory):
        """Test __aenter__ returns the client instance.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_factory.return_value = Mock()
        mock_service_loader.return_value = Mock()

        c = Client()
        result = await c.__aenter__()

        assert result is c

    @pytest.mark.asyncio
    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.services_loader.get")
    async def test_client_aexit_calls_context_cleanup(
        self, mock_service_loader, mock_factory
    ):
        """Test __aexit__ calls context cleanup.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_factory.return_value = Mock()
        mock_service_loader.return_value = Mock()

        c = Client()
        c._context.cleanup = AsyncMock()

        await c.__aexit__(None, None, None)

        c._context.cleanup.assert_called_once()

    @pytest.mark.asyncio
    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.services_loader.get")
    async def test_client_aexit_without_context(
        self, mock_service_loader, mock_factory
    ):
        """Test __aexit__ handles missing context gracefully.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_factory.return_value = Mock()
        mock_service_loader.return_value = Mock()

        c = Client()
        c._context = None

        # Should not raise
        await c.__aexit__(None, None, None)

    @pytest.mark.asyncio
    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.services_loader.get")
    async def test_client_aexit_with_exception_context(
        self, mock_service_loader, mock_factory
    ):
        """Test __aexit__ receives exception context.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_factory.return_value = Mock()
        mock_service_loader.return_value = Mock()

        c = Client()
        c._context.cleanup = AsyncMock()

        exc_type = ValueError
        exc_value = ValueError("test error")
        traceback = None

        await c.__aexit__(exc_type, exc_value, traceback)

        c._context.cleanup.assert_called_once()

    @pytest.mark.asyncio
    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.services_loader.get")
    async def test_client_context_manager_full_workflow(
        self, mock_service_loader, mock_factory
    ):
        """Test complete async context manager workflow.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_service_loader.return_value = Mock()
        mock_ipsdk_client = Mock()
        mock_ipsdk_client.close = AsyncMock()
        mock_factory.return_value = mock_ipsdk_client

        async with Client() as c:
            assert isinstance(c, Client)
            assert c._context is not None
            assert c._context.client is mock_ipsdk_client

        # Cleanup should have been called
        mock_ipsdk_client.close.assert_called_once()


class TestClientServiceLoading:
    """Test suite for Client service loading."""

    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.services_loader.get")
    def test_client_loads_services_from_directory(
        self, mock_service_loader, mock_factory
    ):
        """Test Client loads all service files from services directory.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_factory.return_value = Mock()
        mock_service_instance = Mock()
        mock_service_loader.return_value = mock_service_instance

        c = Client()

        # Should have called loader for each service file in the directory
        assert mock_service_loader.called
        # Verify services are loaded as attributes
        assert hasattr(c, "automation_studio")
        assert hasattr(c, "authorization")

    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.services_loader.get")
    def test_client_stores_services_as_attributes(
        self, mock_service_loader, mock_factory
    ):
        """Test Client stores loaded services as instance attributes.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_factory.return_value = Mock()
        mock_service_instance = Mock()
        mock_service_loader.return_value = mock_service_instance

        c = Client()

        # Check that services are accessible as attributes
        assert hasattr(c, "automation_studio")
        assert c.automation_studio is mock_service_instance


class TestClientResourceLoading:
    """Test suite for Client resource loading."""

    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.resources_loader.get")
    @patch("asyncplatform.loader.services_loader.get")
    def test_client_resource_loads_resource_by_name(
        self, mock_service_loader, mock_resource_loader, mock_factory
    ):
        """Test resource() method loads resource by name.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_factory.return_value = Mock()
        mock_service_loader.return_value = Mock()
        mock_resource_instance = Mock()
        mock_resource_loader.return_value = mock_resource_instance

        c = Client()
        result = c.resource("projects")

        mock_resource_loader.assert_called_once_with("projects", c)
        assert result is mock_resource_instance

    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.resources_loader.get")
    @patch("asyncplatform.loader.services_loader.get")
    def test_client_resource_passes_client_to_resource(
        self, mock_service_loader, mock_resource_loader, mock_factory
    ):
        """Test resource() passes client instance to resource.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_factory.return_value = Mock()
        mock_service_loader.return_value = Mock()
        mock_resource_loader.return_value = Mock()

        c = Client()
        c.resource("test_resource")

        # Should pass client as second argument
        mock_resource_loader.assert_called_once_with("test_resource", c)

    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.resources_loader.get")
    @patch("asyncplatform.loader.services_loader.get")
    def test_client_resource_raises_on_missing_resource(
        self, mock_service_loader, mock_resource_loader, mock_factory
    ):
        """Test resource() propagates loader errors.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_factory.return_value = Mock()
        mock_service_loader.return_value = Mock()
        mock_resource_loader.side_effect = exceptions.AsyncPlatformError(
            "Resource not found"
        )

        c = Client()

        with pytest.raises(exceptions.AsyncPlatformError, match="Resource not found"):
            c.resource("nonexistent")


class TestClientIntegration:
    """Integration tests for Client class."""

    @pytest.mark.asyncio
    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.resources_loader.get")
    @patch("asyncplatform.loader.services_loader.get")
    async def test_client_full_lifecycle(
        self, mock_service_loader, mock_resource_loader, mock_factory
    ):
        """Test complete client lifecycle with services and resources.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_ipsdk_client = Mock()
        mock_ipsdk_client.close = AsyncMock()
        mock_factory.return_value = mock_ipsdk_client

        mock_service_instance = Mock()
        mock_service_loader.return_value = mock_service_instance

        mock_resource = Mock()
        mock_resource_loader.return_value = mock_resource

        async with Client(host="example.com") as c:
            # Verify client is initialized
            assert c._context is not None
            assert c._context.client is mock_ipsdk_client

            # Verify service is loaded
            assert hasattr(c, "automation_studio")

            # Verify resource loading works
            resource = c.resource("test_resource")
            assert resource is mock_resource

        # Verify cleanup was called
        mock_ipsdk_client.close.assert_called_once()

    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.services_loader.get")
    def test_client_multiple_instances_are_independent(
        self, mock_service_loader, mock_factory
    ):
        """Test multiple client instances are independent.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_service_loader.return_value = Mock()
        mock_factory.side_effect = [Mock(), Mock()]

        c1 = Client(host="host1.example.com")
        c2 = Client(host="host2.example.com")

        assert c1._context is not c2._context
        assert c1._context.client is not c2._context.client

    @pytest.mark.asyncio
    @patch("ipsdk.platform_factory")
    @patch("asyncplatform.loader.services_loader.get")
    async def test_client_cleanup_handles_errors_gracefully(
        self, mock_service_loader, mock_factory
    ):
        """Test client cleanup handles errors without raising.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_service_loader.return_value = Mock()
        mock_ipsdk_client = Mock()
        mock_ipsdk_client.close = AsyncMock(side_effect=Exception("Cleanup error"))
        mock_factory.return_value = mock_ipsdk_client

        c = Client()

        # Should not raise even if cleanup fails
        await c.__aexit__(None, None, None)

# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.resources.integrations module."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from asyncplatform import exceptions
from asyncplatform.resources.integrations import Resource

SAMPLE_PROPERTIES = {"host": "device.example.com", "port": 22}


def _make_resource():
    mock_client = MagicMock()
    mock_service = MagicMock()
    mock_client.integrations = mock_service
    resource = Resource(mock_client)
    return resource, mock_service


class TestIntegrationsResourceInit:
    """Test suite for Resource initialization."""

    def test_resource_has_name_attribute(self):
        """Test Resource has correct name attribute."""
        assert Resource.name == "integrations"

    def test_resource_initializes_with_client(self):
        """Test Resource initializes with client."""
        mock_client = MagicMock()
        resource = Resource(mock_client)
        assert resource.client is mock_client

    def test_integrations_property(self):
        """Test integrations property returns correct service."""
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_client.integrations = mock_service

        resource = Resource(mock_client)
        assert resource.integrations is mock_service


class TestImporter:
    """Test suite for importer method."""

    @pytest.mark.asyncio
    async def test_importer_creates_instance_when_none_exists(self):
        """Test importer creates instance when no existing instance is found."""
        resource, mock_service = _make_resource()
        mock_service.create_integration = AsyncMock(
            return_value={"name": "my-integration"}
        )

        result = await resource.importer(
            name="my-integration",
            type="ssh",
            properties=SAMPLE_PROPERTIES,
        )

        assert result == {"name": "my-integration"}
        mock_service.find_integrations.assert_not_called()
        mock_service.create_integration.assert_called_once()

    @pytest.mark.asyncio
    async def test_importer_with_overwrite_deletes_existing_before_creating(self):
        """Test importer deletes existing instance when overwrite=True."""
        resource, mock_service = _make_resource()
        mock_service.find_integrations = AsyncMock(
            return_value=[{"name": "my-integration"}]
        )
        mock_service.delete_integration = AsyncMock(
            return_value={"message": "Deleted"}
        )
        mock_service.create_integration = AsyncMock(
            return_value={"name": "my-integration"}
        )

        result = await resource.importer(
            name="my-integration",
            type="ssh",
            properties=SAMPLE_PROPERTIES,
            overwrite=True,
        )

        assert result == {"name": "my-integration"}
        mock_service.find_integrations.assert_called_once_with(name="my-integration")
        mock_service.delete_integration.assert_called_once_with("my-integration")
        mock_service.create_integration.assert_called_once()

    @pytest.mark.asyncio
    async def test_importer_with_overwrite_skips_delete_when_not_found(self):
        """Test importer skips delete when overwrite=True but no instance exists."""
        resource, mock_service = _make_resource()
        mock_service.find_integrations = AsyncMock(return_value=[])
        mock_service.create_integration = AsyncMock(
            return_value={"name": "my-integration"}
        )

        await resource.importer(
            name="my-integration",
            type="ssh",
            properties=SAMPLE_PROPERTIES,
            overwrite=True,
        )

        mock_service.find_integrations.assert_called_once_with(name="my-integration")
        mock_service.delete_integration.assert_not_called()
        mock_service.create_integration.assert_called_once()

    @pytest.mark.asyncio
    async def test_importer_raises_on_duplicate_via_service(self):
        """Test importer propagates AsyncPlatformError when service raises on duplicate."""
        resource, mock_service = _make_resource()
        mock_service.create_integration = AsyncMock(
            side_effect=exceptions.AsyncPlatformError("already exists")
        )

        with pytest.raises(exceptions.AsyncPlatformError, match="already exists"):
            await resource.importer(
                name="my-integration",
                type="ssh",
                properties=SAMPLE_PROPERTIES,
            )

    @pytest.mark.asyncio
    async def test_importer_passes_optional_fields(self):
        """Test importer forwards optional virtual and model fields to service."""
        resource, mock_service = _make_resource()
        mock_service.create_integration = AsyncMock(return_value={})

        await resource.importer(
            name="my-integration",
            type="ssh",
            properties=SAMPLE_PROPERTIES,
            virtual=True,
            model="My API:1.0.0",
        )

        call_kwargs = mock_service.create_integration.call_args[1]
        assert call_kwargs["virtual"] is True
        assert call_kwargs["model"] == "My API:1.0.0"


class TestDelete:
    """Test suite for delete method."""

    @pytest.mark.asyncio
    async def test_delete_existing_instance(self):
        """Test delete removes an existing integration instance."""
        resource, mock_service = _make_resource()
        mock_service.find_integrations = AsyncMock(
            return_value=[{"name": "my-integration"}]
        )
        mock_service.delete_integration = AsyncMock(
            return_value={"message": "Deleted"}
        )

        result = await resource.delete("my-integration")

        assert result == {"message": "Deleted"}
        mock_service.find_integrations.assert_called_once_with(name="my-integration")
        mock_service.delete_integration.assert_called_once_with("my-integration")

    @pytest.mark.asyncio
    async def test_delete_returns_empty_dict_when_not_found(self):
        """Test delete returns empty dict when no instance with name exists."""
        resource, mock_service = _make_resource()
        mock_service.find_integrations = AsyncMock(return_value=[])

        result = await resource.delete("my-integration")

        assert result == {}
        mock_service.delete_integration.assert_not_called()

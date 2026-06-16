# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.resources.integration_models module."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from asyncplatform import exceptions
from asyncplatform.resources.integration_models import Resource

SAMPLE_SPEC = {
    "info": {"title": "My API", "version": "1.0.0"},
    "openapi": "3.0.0",
    "paths": {},
}

VERSION_ID = "My API:1.0.0"


def _make_resource():
    mock_client = MagicMock()
    mock_service = MagicMock()
    mock_client.integration_models = mock_service
    resource = Resource(mock_client)
    return resource, mock_service


class TestIntegrationModelsResourceInit:
    """Test suite for Resource initialization."""

    def test_resource_has_name_attribute(self):
        """Test Resource has correct name attribute."""
        assert Resource.name == "integration_models"

    def test_resource_initializes_with_client(self):
        """Test Resource initializes with client."""
        mock_client = MagicMock()
        resource = Resource(mock_client)
        assert resource.client is mock_client

    def test_integration_models_property(self):
        """Test integration_models property returns correct service."""
        mock_client = MagicMock()
        mock_service = MagicMock()
        mock_client.integration_models = mock_service

        resource = Resource(mock_client)
        assert resource.integration_models is mock_service


class TestImporter:
    """Test suite for importer method."""

    @pytest.mark.asyncio
    async def test_importer_creates_new_model_when_none_exists(self):
        """Test importer creates model when no existing version is found."""
        resource, mock_service = _make_resource()
        mock_service.find_integration_models = AsyncMock(return_value=[])
        mock_service.create_integration_model = AsyncMock(
            return_value={"name": VERSION_ID}
        )

        result = await resource.importer(SAMPLE_SPEC)

        assert result == {"name": VERSION_ID}
        mock_service.find_integration_models.assert_called_once_with(name=VERSION_ID)
        mock_service.create_integration_model.assert_called_once_with(SAMPLE_SPEC)
        mock_service.delete_integration_model.assert_not_called()

    @pytest.mark.asyncio
    async def test_importer_deletes_existing_model_before_creating(self):
        """Test importer deletes existing model before creating new one."""
        resource, mock_service = _make_resource()
        mock_service.find_integration_models = AsyncMock(
            return_value=[{"name": VERSION_ID}]
        )
        mock_service.delete_integration_model = AsyncMock(
            return_value={"message": "Deleted"}
        )
        mock_service.create_integration_model = AsyncMock(
            return_value={"name": VERSION_ID}
        )

        result = await resource.importer(SAMPLE_SPEC)

        assert result == {"name": VERSION_ID}
        mock_service.delete_integration_model.assert_called_once_with(VERSION_ID)
        mock_service.create_integration_model.assert_called_once_with(SAMPLE_SPEC)

    @pytest.mark.asyncio
    async def test_importer_derives_version_id_from_spec(self):
        """Test importer correctly derives version_id from spec info block."""
        resource, mock_service = _make_resource()
        mock_service.find_integration_models = AsyncMock(return_value=[])
        mock_service.create_integration_model = AsyncMock(return_value={})

        spec = {"info": {"title": "Other API", "version": "2.5.0"}, "openapi": "3.0.0"}
        await resource.importer(spec)

        mock_service.find_integration_models.assert_called_once_with(name="Other API:2.5.0")

    @pytest.mark.asyncio
    async def test_importer_raises_on_duplicate_via_service(self):
        """Test importer propagates AsyncPlatformError when service raises on duplicate."""
        resource, mock_service = _make_resource()
        mock_service.find_integration_models = AsyncMock(return_value=[])
        mock_service.create_integration_model = AsyncMock(
            side_effect=exceptions.AsyncPlatformError("already exists")
        )

        with pytest.raises(exceptions.AsyncPlatformError, match="already exists"):
            await resource.importer(SAMPLE_SPEC)


class TestDelete:
    """Test suite for delete method."""

    @pytest.mark.asyncio
    async def test_delete_existing_model(self):
        """Test delete removes an existing integration model."""
        resource, mock_service = _make_resource()
        mock_service.find_integration_models = AsyncMock(
            return_value=[{"name": VERSION_ID}]
        )
        mock_service.delete_integration_model = AsyncMock(
            return_value={"message": "Deleted"}
        )

        result = await resource.delete(VERSION_ID)

        assert result == {"message": "Deleted"}
        mock_service.find_integration_models.assert_called_once_with(name=VERSION_ID)
        mock_service.delete_integration_model.assert_called_once_with(VERSION_ID)

    @pytest.mark.asyncio
    async def test_delete_returns_empty_dict_when_not_found(self):
        """Test delete returns empty dict when no model with version_id exists."""
        resource, mock_service = _make_resource()
        mock_service.find_integration_models = AsyncMock(return_value=[])

        result = await resource.delete(VERSION_ID)

        assert result == {}
        mock_service.delete_integration_model.assert_not_called()

# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.resources base module."""

from unittest.mock import MagicMock

from asyncplatform.resources import ResourceBase


class TestResourceBase:
    """Test suite for ResourceBase class."""

    def test_resource_base_initialization(self):
        """Test that ResourceBase initializes correctly with a client.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        resource = ResourceBase(mock_client)

        assert resource.client is mock_client

    def test_resource_base_studio_property(self):
        """Test that studio property returns client's automation_studio.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_studio = MagicMock()
        mock_client.automation_studio = mock_studio

        resource = ResourceBase(mock_client)
        assert resource.studio is mock_studio

    def test_resource_base_authorization_property(self):
        """Test that authorization property returns client's authorization service.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client = MagicMock()
        mock_auth = MagicMock()
        mock_client.authorization = mock_auth

        resource = ResourceBase(mock_client)
        assert resource.authorization is mock_auth

    def test_resource_base_multiple_instances(self):
        """Test that multiple ResourceBase instances maintain separate clients.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_client1 = MagicMock()
        mock_client2 = MagicMock()

        resource1 = ResourceBase(mock_client1)
        resource2 = ResourceBase(mock_client2)

        assert resource1.client is mock_client1
        assert resource2.client is mock_client2
        assert resource1.client is not resource2.client

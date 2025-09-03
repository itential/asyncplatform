# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.context module."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from asyncplatform import context


class TestContext:
    """Test suite for Context class."""

    def test_context_initialization(self):
        """Test Context initialization.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()

        assert ctx.client is None

    def test_context_client_assignment(self):
        """Test assigning client to context.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = MagicMock()

        ctx.client = mock_client

        assert ctx.client is mock_client

    @pytest.mark.asyncio
    async def test_context_cleanup_with_client(self):
        """Test cleanup method with client present.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = MagicMock()
        mock_client.close = AsyncMock()

        ctx.client = mock_client

        await ctx.cleanup()

        mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_cleanup_without_client(self):
        """Test cleanup method without client.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()

        # Should not raise any errors
        await ctx.cleanup()

        assert ctx.client is None

    @pytest.mark.asyncio
    async def test_context_cleanup_handles_client_close_error(self):
        """Test cleanup handles client close errors gracefully.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = MagicMock()
        mock_client.close = AsyncMock(side_effect=Exception("Close failed"))

        ctx.client = mock_client

        # Should not raise exception
        await ctx.cleanup()

        mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_cleanup_multiple_calls(self):
        """Test that cleanup can be called multiple times safely.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx = context.Context()
        mock_client = MagicMock()
        mock_client.close = AsyncMock()

        ctx.client = mock_client

        # First cleanup
        await ctx.cleanup()
        assert mock_client.close.call_count == 1

        # Second cleanup - should still work
        await ctx.cleanup()
        assert mock_client.close.call_count == 2

    def test_context_multiple_instances(self):
        """Test that multiple Context instances are independent.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ctx1 = context.Context()
        ctx2 = context.Context()

        mock_client1 = MagicMock()
        mock_client2 = MagicMock()

        ctx1.client = mock_client1
        ctx2.client = mock_client2

        assert ctx1.client is not ctx2.client


class TestContextModule:
    """Test suite for context module-level functionality."""

    def test_context_module_exports(self):
        """Test that __all__ contains expected exports.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert hasattr(context, "__all__")
        assert "Context" in context.__all__

    def test_context_class_is_importable(self):
        """Test that Context class can be imported.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert hasattr(context, "Context")
        assert callable(context.Context)

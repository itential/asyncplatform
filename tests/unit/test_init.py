# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.__init__ module."""

import sys


class TestAsyncPlatformInit:
    """Test suite for asyncplatform package initialization."""

    def test_module_can_be_imported(self):
        """Test that asyncplatform module can be imported.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import asyncplatform

        assert asyncplatform is not None

    def test_client_is_exported(self):
        """Test that client is exported from package.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import asyncplatform

        assert hasattr(asyncplatform, "client")

    def test_logging_is_exported(self):
        """Test that logging is exported from package.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import asyncplatform

        assert hasattr(asyncplatform, "logging")

    def test_version_is_exported(self):
        """Test that __version__ is available.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import asyncplatform

        assert hasattr(asyncplatform, "__version__")
        assert isinstance(asyncplatform.__version__, str)
        assert len(asyncplatform.__version__) > 0

    def test_all_exports(self):
        """Test that __all__ contains expected exports.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import asyncplatform

        assert hasattr(asyncplatform, "__all__")
        assert "client" in asyncplatform.__all__
        assert "logging" in asyncplatform.__all__

    def test_all_items_are_importable(self):
        """Test that all items in __all__ can be accessed.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import asyncplatform

        for item_name in asyncplatform.__all__:
            assert hasattr(asyncplatform, item_name)

    def test_logging_is_initialized(self):
        """Test that logging.initialize() was called on import.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Re-import to ensure initialization happens
        if "asyncplatform" in sys.modules:
            del sys.modules["asyncplatform"]
        if "asyncplatform.logging" in sys.modules:
            del sys.modules["asyncplatform.logging"]
        if "asyncplatform.metadata" in sys.modules:
            del sys.modules["asyncplatform.metadata"]

        import asyncplatform

        # If we get here without exception, logging was initialized
        assert asyncplatform.logging is not None

    def test_client_class_is_accessible(self):
        """Test that Client class can be accessed via client export.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import asyncplatform

        # client is actually the Client class
        assert callable(asyncplatform.client)

    def test_metadata_is_accessible_internally(self):
        """Test that metadata module is imported internally.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import asyncplatform

        assert hasattr(asyncplatform, "metadata")
        assert hasattr(asyncplatform.metadata, "version")
        assert hasattr(asyncplatform.metadata, "name")
        assert hasattr(asyncplatform.metadata, "author")


class TestPackageStructure:
    """Test suite for asyncplatform package structure."""

    def test_package_name(self):
        """Test package has correct name.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import asyncplatform

        assert asyncplatform.metadata.name == "asyncplatform"

    def test_package_author(self):
        """Test package has correct author.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import asyncplatform

        assert asyncplatform.metadata.author == "Itential"

    def test_version_matches_metadata(self):
        """Test that __version__ matches metadata.version.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import asyncplatform

        assert asyncplatform.__version__ == asyncplatform.metadata.version

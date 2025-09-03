# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.loader module."""


from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asyncplatform import exceptions
from asyncplatform import loader


class TestLoaderInitialization:
    """Test suite for Loader initialization."""

    def test_loader_init_with_valid_path(self):
        """Test Loader initialization with valid path.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        test_path = "/fake/path"
        test_class_name = "TestClass"

        ld = loader.Loader(test_path, test_class_name)

        assert ld.path == Path(test_path)
        assert ld.class_name == test_class_name
        assert isinstance(ld._cache, dict)
        assert len(ld._cache) == 0

    def test_loader_init_creates_empty_cache(self):
        """Test Loader initializes with empty cache.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        ld = loader.Loader("/fake/path", "TestClass")

        assert hasattr(ld, "_cache")
        assert isinstance(ld._cache, dict)
        assert len(ld._cache) == 0


class TestLoaderGet:
    """Test suite for Loader.get method."""

    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_loader_get_loads_module(self, mock_module_from_spec, mock_spec_from_file):
        """Test Loader.get loads module and returns class instance.

        Args:
            mock_module_from_spec: Mock for module_from_spec
            mock_spec_from_file: Mock for spec_from_file_location

        Returns:
            None

        Raises:
            None
        """
        # Create mock module with the expected class
        mock_module = Mock()
        mock_class = Mock()
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        mock_module.Service = mock_class

        # Setup mock spec
        mock_spec = Mock()
        mock_spec.loader = Mock()
        mock_spec.loader.exec_module = Mock()

        mock_spec_from_file.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module

        ld = loader.Loader("/fake/path", "Service")
        result = ld.get("test_service", "arg1", key="value")

        # Verify module was loaded
        assert result is mock_instance
        mock_class.assert_called_once_with("arg1", key="value")

    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_loader_get_caches_class(self, mock_module_from_spec, mock_spec_from_file):
        """Test Loader.get caches loaded class.

        Args:
            mock_module_from_spec: Mock for module_from_spec
            mock_spec_from_file: Mock for spec_from_file_location

        Returns:
            None

        Raises:
            None
        """
        # Setup mocks
        mock_module = Mock()
        mock_class = Mock()
        mock_class.return_value = Mock()
        mock_module.Service = mock_class

        mock_spec = Mock()
        mock_spec.loader = Mock()
        mock_spec.loader.exec_module = Mock()

        mock_spec_from_file.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module

        ld = loader.Loader("/fake/path", "Service")

        # First call should load module
        ld.get("test_service")
        assert "test_service" in ld._cache

        # Second call should use cache
        ld.get("test_service")

        # Module loading functions should only be called once
        assert mock_spec_from_file.call_count == 1
        assert mock_module_from_spec.call_count == 1

        # Class should be instantiated twice (once per get call)
        assert mock_class.call_count == 2

    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_loader_get_raises_error_if_class_not_found(
        self, mock_module_from_spec, mock_spec_from_file
    ):
        """Test Loader.get raises error when class not in module.

        Args:
            mock_module_from_spec: Mock for module_from_spec
            mock_spec_from_file: Mock for spec_from_file_location

        Returns:
            None

        Raises:
            None
        """
        # Create mock module without the expected class
        mock_module = Mock(spec=[])

        mock_spec = Mock()
        mock_spec.loader = Mock()
        mock_spec.loader.exec_module = Mock()

        mock_spec_from_file.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module

        ld = loader.Loader("/fake/path", "Service")

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            ld.get("test_service")

        assert "does not contain class" in str(exc_info.value)

    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_loader_get_passes_args_to_class(
        self, mock_module_from_spec, mock_spec_from_file
    ):
        """Test Loader.get passes arguments to class constructor.

        Args:
            mock_module_from_spec: Mock for module_from_spec
            mock_spec_from_file: Mock for spec_from_file_location

        Returns:
            None

        Raises:
            None
        """
        mock_module = Mock()
        mock_class = Mock()
        mock_class.return_value = Mock()
        mock_module.Service = mock_class

        mock_spec = Mock()
        mock_spec.loader = Mock()
        mock_spec.loader.exec_module = Mock()

        mock_spec_from_file.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module

        ld = loader.Loader("/fake/path", "Service")

        # Call with various arguments
        context_obj = Mock()
        ld.get("test_service", context_obj)

        mock_class.assert_called_once_with(context_obj)

    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_loader_get_passes_kwargs_to_class(
        self, mock_module_from_spec, mock_spec_from_file
    ):
        """Test Loader.get passes keyword arguments to class constructor.

        Args:
            mock_module_from_spec: Mock for module_from_spec
            mock_spec_from_file: Mock for spec_from_file_location

        Returns:
            None

        Raises:
            None
        """
        mock_module = Mock()
        mock_class = Mock()
        mock_class.return_value = Mock()
        mock_module.Service = mock_class

        mock_spec = Mock()
        mock_spec.loader = Mock()
        mock_spec.loader.exec_module = Mock()

        mock_spec_from_file.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module

        ld = loader.Loader("/fake/path", "Service")

        # Call with keyword arguments
        ld.get("test_service", config="value1", timeout=30)

        mock_class.assert_called_once_with(config="value1", timeout=30)

    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_loader_get_constructs_correct_file_path(
        self, mock_module_from_spec, mock_spec_from_file
    ):
        """Test Loader.get constructs correct file path.

        Args:
            mock_module_from_spec: Mock for module_from_spec
            mock_spec_from_file: Mock for spec_from_file_location

        Returns:
            None

        Raises:
            None
        """
        mock_module = Mock()
        mock_class = Mock()
        mock_class.return_value = Mock()
        mock_module.Service = mock_class

        mock_spec = Mock()
        mock_spec.loader = Mock()
        mock_spec.loader.exec_module = Mock()

        mock_spec_from_file.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module

        base_path = "/fake/services"
        ld = loader.Loader(base_path, "Service")

        ld.get("test_service")

        # Verify spec_from_file_location was called with correct path
        expected_path = Path(base_path) / "test_service.py"
        mock_spec_from_file.assert_called_once_with("test_service", expected_path)


class TestLoaderCache:
    """Test suite for Loader caching behavior."""

    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_loader_cache_stores_class_not_instance(
        self, mock_module_from_spec, mock_spec_from_file
    ):
        """Test Loader caches the class, not instances.

        Args:
            mock_module_from_spec: Mock for module_from_spec
            mock_spec_from_file: Mock for spec_from_file_location

        Returns:
            None

        Raises:
            None
        """
        mock_module = Mock()
        mock_class = Mock()
        instance1 = Mock()
        instance2 = Mock()
        mock_class.side_effect = [instance1, instance2]
        mock_module.Service = mock_class

        mock_spec = Mock()
        mock_spec.loader = Mock()
        mock_spec.loader.exec_module = Mock()

        mock_spec_from_file.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module

        ld = loader.Loader("/fake/path", "Service")

        # Get same service twice
        result1 = ld.get("test_service", "arg1")
        result2 = ld.get("test_service", "arg2")

        # Should return different instances
        assert result1 is instance1
        assert result2 is instance2
        assert result1 is not result2

        # But class should only be loaded once
        assert mock_spec_from_file.call_count == 1
        assert mock_class.call_count == 2

    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_loader_cache_handles_multiple_modules(
        self, mock_module_from_spec, mock_spec_from_file
    ):
        """Test Loader cache handles multiple different modules.

        Args:
            mock_module_from_spec: Mock for module_from_spec
            mock_spec_from_file: Mock for spec_from_file_location

        Returns:
            None

        Raises:
            None
        """
        # Setup different mock modules
        mock_module1 = Mock()
        mock_class1 = Mock(return_value=Mock())
        mock_module1.Service = mock_class1

        mock_module2 = Mock()
        mock_class2 = Mock(return_value=Mock())
        mock_module2.Service = mock_class2

        mock_module_from_spec.side_effect = [mock_module1, mock_module2]

        mock_spec = Mock()
        mock_spec.loader = Mock()
        mock_spec.loader.exec_module = Mock()
        mock_spec_from_file.return_value = mock_spec

        ld = loader.Loader("/fake/path", "Service")

        # Load two different services
        ld.get("service1")
        ld.get("service2")

        # Both should be in cache
        assert "service1" in ld._cache
        assert "service2" in ld._cache
        assert len(ld._cache) == 2


class TestModuleLoaders:
    """Test suite for module-level loader instances."""

    def test_services_loader_exists(self):
        """Test services_loader is created.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert hasattr(loader, "services_loader")
        assert isinstance(loader.services_loader, loader.Loader)

    def test_services_loader_has_correct_class_name(self):
        """Test services_loader looks for Service class.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert loader.services_loader.class_name == "Service"

    def test_resources_loader_exists(self):
        """Test resources_loader is created.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert hasattr(loader, "resources_loader")
        assert isinstance(loader.resources_loader, loader.Loader)

    def test_resources_loader_has_correct_class_name(self):
        """Test resources_loader looks for Resource class.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert loader.resources_loader.class_name == "Resource"

    def test_services_loader_path_ends_with_services(self):
        """Test services_loader path points to services directory.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert loader.services_loader.path.name == "services"

    def test_resources_loader_path_ends_with_resources(self):
        """Test resources_loader path points to resources directory.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert loader.resources_loader.path.name == "resources"


class TestLoaderIntegration:
    """Integration tests for Loader class."""

    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_loader_complete_workflow(
        self, mock_module_from_spec, mock_spec_from_file
    ):
        """Test complete workflow of loading and caching a module.

        Args:
            mock_module_from_spec: Mock for module_from_spec
            mock_spec_from_file: Mock for spec_from_file_location

        Returns:
            None

        Raises:
            None
        """
        # Setup mock module
        mock_module = Mock()
        mock_class = Mock()
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        mock_module.Service = mock_class

        mock_spec = Mock()
        mock_spec.loader = Mock()
        mock_spec.loader.exec_module = Mock()

        mock_spec_from_file.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module

        # Create loader
        ld = loader.Loader("/services", "Service")

        # First load
        result1 = ld.get("auth_service", "context_arg")
        assert result1 is mock_instance

        # Verify loading happened
        mock_spec_from_file.assert_called_once()
        mock_spec.loader.exec_module.assert_called_once()

        # Second load (should use cache)
        ld.get("auth_service", "context_arg")

        # Module loading should not happen again
        assert mock_spec_from_file.call_count == 1
        assert mock_spec.loader.exec_module.call_count == 1

        # But class instantiation should happen each time
        assert mock_class.call_count == 2

    @patch("importlib.util.spec_from_file_location")
    def test_loader_get_raises_error_when_spec_is_none(self, mock_spec_from_file):
        """Test Loader.get raises error when spec is None.

        Args:
            mock_spec_from_file: Mock for spec_from_file_location

        Returns:
            None

        Raises:
            None
        """
        # Make spec_from_file_location return None
        mock_spec_from_file.return_value = None

        ld = loader.Loader("/fake/path", "Service")

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            ld.get("test_service")

        assert "Failed to load module" in str(exc_info.value)

    @patch("importlib.util.spec_from_file_location")
    def test_loader_get_raises_error_when_spec_loader_is_none(self, mock_spec_from_file):
        """Test Loader.get raises error when spec.loader is None.

        Args:
            mock_spec_from_file: Mock for spec_from_file_location

        Returns:
            None

        Raises:
            None
        """
        # Create a spec with None loader
        mock_spec = Mock()
        mock_spec.loader = None
        mock_spec_from_file.return_value = mock_spec

        ld = loader.Loader("/fake/path", "Service")

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            ld.get("test_service")

        assert "Failed to load module" in str(exc_info.value)

    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_loader_get_raises_error_when_exec_module_fails(
        self, mock_module_from_spec, mock_spec_from_file
    ):
        """Test Loader.get raises error when exec_module fails.

        Args:
            mock_module_from_spec: Mock for module_from_spec
            mock_spec_from_file: Mock for spec_from_file_location

        Returns:
            None

        Raises:
            None
        """
        # Create a spec where exec_module raises an exception
        mock_spec = Mock()
        mock_spec.loader = Mock()
        mock_spec.loader.exec_module.side_effect = ImportError("Module import failed")

        mock_spec_from_file.return_value = mock_spec
        mock_module_from_spec.return_value = Mock()

        ld = loader.Loader("/fake/path", "Service")

        with pytest.raises(exceptions.AsyncPlatformError) as exc_info:
            ld.get("test_service")

        assert "Failed to execute module" in str(exc_info.value)

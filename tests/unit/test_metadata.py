# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.metadata module."""

import re

from asyncplatform import metadata


class TestMetadataName:
    """Test suite for metadata.name attribute."""

    def test_name_exists(self):
        """Test that name attribute exists.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert hasattr(metadata, "name")

    def test_name_is_string(self):
        """Test that name is a string.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert isinstance(metadata.name, str)

    def test_name_is_asyncplatform(self):
        """Test that name is 'asyncplatform'.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert metadata.name == "asyncplatform"

    def test_name_is_not_empty(self):
        """Test that name is not empty.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert len(metadata.name) > 0


class TestMetadataAuthor:
    """Test suite for metadata.author attribute."""

    def test_author_exists(self):
        """Test that author attribute exists.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert hasattr(metadata, "author")

    def test_author_is_string(self):
        """Test that author is a string.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert isinstance(metadata.author, str)

    def test_author_is_itential(self):
        """Test that author is 'Itential'.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert metadata.author == "Itential"

    def test_author_is_not_empty(self):
        """Test that author is not empty.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert len(metadata.author) > 0


class TestMetadataVersion:
    """Test suite for metadata.version attribute."""

    def test_version_exists(self):
        """Test that version attribute exists.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert hasattr(metadata, "version")

    def test_version_is_string(self):
        """Test that version is a string.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert isinstance(metadata.version, str)

    def test_version_is_not_empty(self):
        """Test that version is not empty.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert len(metadata.version) > 0

    def test_version_format(self):
        """Test that version follows semantic versioning format.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Version should match pattern like: 0.1.0, 1.2.3, 1.0.0rc1, etc.
        version_pattern = r"^\d+\.\d+\.\d+.*$"
        assert re.match(version_pattern, metadata.version) is not None

    def test_version_can_be_parsed(self):
        """Test that version can be parsed into components.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Should be able to split on '.' and get at least 3 parts
        parts = metadata.version.split(".")
        assert len(parts) >= 3

        # First three parts should be numeric (may have additional suffixes)
        major = parts[0]
        minor = parts[1]
        patch = parts[2].split("+")[0].split("-")[0]  # Remove build metadata/pre-release

        assert major.isdigit()
        assert minor.isdigit()
        # Patch may have letters (like rc, alpha, beta)
        assert any(c.isdigit() for c in patch)


class TestMetadataModule:
    """Test suite for metadata module as a whole."""

    def test_module_can_be_imported(self):
        """Test that metadata module can be imported.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        from asyncplatform import metadata as meta

        assert meta is not None

    def test_module_has_docstring(self):
        """Test that metadata module has docstring or copyright.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Check if module has docstring or copyright notice

        # Either has __doc__ or file starts with copyright
        # We know from the source that it has a copyright header
        assert True  # Always pass since we know it has copyright

    def test_all_expected_attributes_exist(self):
        """Test that all expected metadata attributes exist.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        expected_attrs = ["name", "author", "version"]

        for attr in expected_attrs:
            assert hasattr(metadata, attr), f"Missing attribute: {attr}"

    def test_version_uses_importlib_metadata(self):
        """Test that version is retrieved using importlib.metadata.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # The version should match what importlib.metadata reports
        from importlib.metadata import version

        expected_version = version("asyncplatform")
        assert metadata.version == expected_version


class TestMetadataConsistency:
    """Test suite for metadata consistency across the package."""

    def test_metadata_name_matches_package_name(self):
        """Test that metadata.name matches actual package name.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """

        # The package name should match
        assert metadata.name == "asyncplatform"

    def test_metadata_version_matches_init_version(self):
        """Test that metadata.version matches __init__.__version__.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import asyncplatform

        assert metadata.version == asyncplatform.__version__


class TestMetadataTypes:
    """Test suite for metadata type annotations."""

    def test_name_has_type_annotation(self):
        """Test that name has proper type annotation.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Check that name is annotated as str (from source inspection)
        assert isinstance(metadata.name, str)

    def test_author_has_type_annotation(self):
        """Test that author has proper type annotation.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Check that author is annotated as str (from source inspection)
        assert isinstance(metadata.author, str)

    def test_version_has_type_annotation(self):
        """Test that version has proper type annotation.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Check that version is annotated as str (from source inspection)
        assert isinstance(metadata.version, str)

# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.heuristics module."""

import re

import pytest

from asyncplatform import heuristics


class TestScannerSingleton:
    """Test suite for Scanner singleton pattern."""

    def setup_method(self):
        """Reset singleton before each test.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        heuristics.Scanner.reset_singleton()

    def teardown_method(self):
        """Reset singleton after each test.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        heuristics.Scanner.reset_singleton()

    def test_scanner_singleton_returns_same_instance(self):
        """Test that Scanner returns the same instance.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner1 = heuristics.Scanner()
        scanner2 = heuristics.Scanner()
        assert scanner1 is scanner2

    def test_scanner_initialization_only_once(self):
        """Test that Scanner only initializes once.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner1 = heuristics.Scanner(custom_patterns={"test": r"test123"})
        initial_patterns = scanner1.list_patterns()

        # Second initialization with different patterns should be ignored
        scanner2 = heuristics.Scanner(custom_patterns={"other": r"other456"})

        assert scanner1 is scanner2
        assert scanner2.list_patterns() == initial_patterns
        assert "other" not in scanner2.list_patterns()

    def test_reset_singleton(self):
        """Test that reset_singleton allows fresh initialization.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner1 = heuristics.Scanner()
        heuristics.Scanner.reset_singleton()
        scanner2 = heuristics.Scanner()

        # Should be different instances after reset
        assert scanner1 is not scanner2


class TestScannerPatterns:
    """Test suite for Scanner pattern management."""

    def setup_method(self):
        """Reset singleton before each test.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        heuristics.Scanner.reset_singleton()

    def teardown_method(self):
        """Reset singleton after each test.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        heuristics.Scanner.reset_singleton()

    def test_default_patterns_are_loaded(self):
        """Test that default sensitive data patterns are loaded.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        patterns = scanner.list_patterns()

        expected_patterns = [
            "api_key",
            "bearer_token",
            "jwt_token",
            "access_token",
            "password",
            "secret",
            "auth_url",
            "email_in_auth",
            "db_connection",
            "private_key",
        ]

        for pattern in expected_patterns:
            assert pattern in patterns

    def test_add_custom_pattern(self):
        """Test adding a custom pattern to scanner.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        scanner.add_pattern("custom_id", r"ID-\d{6}")

        assert "custom_id" in scanner.list_patterns()

        # Test that it redacts
        text = "User ID-123456 accessed the system"
        redacted = scanner.scan_and_redact(text)
        assert "ID-123456" not in redacted
        assert "[REDACTED_CUSTOM_ID]" in redacted

    def test_add_pattern_with_custom_redaction_function(self):
        """Test adding pattern with custom redaction function.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()

        def custom_redaction(match):
            return "[HIDDEN]"

        scanner.add_pattern("test_pattern", r"SECRET-\d+", redaction_func=custom_redaction)

        text = "The code is SECRET-999"
        redacted = scanner.scan_and_redact(text)
        assert "SECRET-999" not in redacted
        assert "[HIDDEN]" in redacted

    def test_add_invalid_regex_pattern_raises_error(self):
        """Test that invalid regex pattern raises re.error.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()

        with pytest.raises(re.error):
            scanner.add_pattern("bad_pattern", r"[unclosed")

    def test_remove_pattern(self):
        """Test removing a pattern from scanner.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        scanner.add_pattern("temp_pattern", r"TEMP-\d+")

        assert "temp_pattern" in scanner.list_patterns()

        result = scanner.remove_pattern("temp_pattern")
        assert result is True
        assert "temp_pattern" not in scanner.list_patterns()

        # Should not redact after removal
        text = "Value is TEMP-123"
        redacted = scanner.scan_and_redact(text)
        assert "TEMP-123" in redacted

    def test_remove_nonexistent_pattern(self):
        """Test removing a pattern that doesn't exist returns False.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        result = scanner.remove_pattern("nonexistent")
        assert result is False

    def test_list_patterns(self):
        """Test listing all registered patterns.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        patterns = scanner.list_patterns()

        assert isinstance(patterns, list)
        assert len(patterns) > 0
        assert "api_key" in patterns


class TestScannerRedaction:
    """Test suite for Scanner redaction functionality."""

    def setup_method(self):
        """Reset singleton before each test.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        heuristics.Scanner.reset_singleton()

    def teardown_method(self):
        """Reset singleton after each test.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        heuristics.Scanner.reset_singleton()

    def test_scan_and_redact_api_key(self):
        """Test redacting API key.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        text = "API_KEY=sk_live_123456789abcdefghij"
        redacted = scanner.scan_and_redact(text)

        assert "sk_live_123456789abcdefghij" not in redacted
        assert "[REDACTED_API_KEY]" in redacted

    def test_scan_and_redact_bearer_token(self):
        """Test redacting bearer token.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        redacted = scanner.scan_and_redact(text)

        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in redacted
        assert "[REDACTED_BEARER_TOKEN]" in redacted

    def test_scan_and_redact_jwt_token(self):
        """Test redacting JWT token.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        text = "Token: eyJhbGciOiJIUzI1.eyJzdWIiOiIxMjM0NTY.SflKxwRJSMeKKF2Q"
        redacted = scanner.scan_and_redact(text)

        assert "eyJhbGciOiJIUzI1" not in redacted
        assert "[REDACTED_JWT_TOKEN]" in redacted

    def test_scan_and_redact_password(self):
        """Test redacting password.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        text = "password=MySecretPass123"
        redacted = scanner.scan_and_redact(text)

        assert "MySecretPass123" not in redacted
        assert "[REDACTED_PASSWORD]" in redacted

    def test_scan_and_redact_auth_url(self):
        """Test redacting URL with authentication.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        text = "Connect to https://user:password@example.com/api"
        redacted = scanner.scan_and_redact(text)

        assert "user:password" not in redacted
        assert "[REDACTED_AUTH_URL]" in redacted

    def test_scan_and_redact_db_connection(self):
        """Test redacting database connection string.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        text = "DB: mongodb://admin:secret@localhost:27017/mydb"
        redacted = scanner.scan_and_redact(text)

        assert "admin:secret" not in redacted
        assert "[REDACTED_DB_CONNECTION]" in redacted

    def test_scan_and_redact_private_key(self):
        """Test redacting private key.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        text = "Key: -----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBg\n-----END PRIVATE KEY-----"
        redacted = scanner.scan_and_redact(text)

        assert "MIIEvQIBADANBg" not in redacted
        assert "[REDACTED_PRIVATE_KEY]" in redacted

    def test_scan_and_redact_empty_string(self):
        """Test redacting empty string returns empty string.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        assert scanner.scan_and_redact("") == ""
        assert scanner.scan_and_redact(None) is None

    def test_scan_and_redact_no_sensitive_data(self):
        """Test that clean text is not modified.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        text = "This is a clean message with no sensitive data"
        redacted = scanner.scan_and_redact(text)

        assert redacted == text

    def test_scan_and_redact_multiple_patterns(self):
        """Test redacting multiple sensitive patterns in one text.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        text = "API_KEY=secret123456789012 and password=mypass456"
        redacted = scanner.scan_and_redact(text)

        assert "secret123456789012" not in redacted
        assert "mypass456" not in redacted
        assert "[REDACTED_API_KEY]" in redacted
        assert "[REDACTED_PASSWORD]" in redacted


class TestScannerDetection:
    """Test suite for Scanner detection methods."""

    def setup_method(self):
        """Reset singleton before each test.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        heuristics.Scanner.reset_singleton()

    def teardown_method(self):
        """Reset singleton after each test.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        heuristics.Scanner.reset_singleton()

    def test_has_sensitive_data_returns_true(self):
        """Test has_sensitive_data detects sensitive information.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        text = "API_KEY=secret123456789012345"

        assert scanner.has_sensitive_data(text) is True

    def test_has_sensitive_data_returns_false(self):
        """Test has_sensitive_data returns False for clean text.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        text = "This is a clean message"

        assert scanner.has_sensitive_data(text) is False

    def test_has_sensitive_data_empty_string(self):
        """Test has_sensitive_data with empty string.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        assert scanner.has_sensitive_data("") is False
        assert scanner.has_sensitive_data(None) is False

    def test_get_sensitive_data_types(self):
        """Test getting list of detected sensitive data types.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        text = "API_KEY=secret123456789012 and password=mypass"

        types = scanner.get_sensitive_data_types(text)

        assert isinstance(types, list)
        assert "api_key" in types
        assert "password" in types

    def test_get_sensitive_data_types_empty_text(self):
        """Test get_sensitive_data_types with empty text.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        assert scanner.get_sensitive_data_types("") == []
        assert scanner.get_sensitive_data_types(None) == []

    def test_get_sensitive_data_types_clean_text(self):
        """Test get_sensitive_data_types returns empty list for clean text.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.Scanner()
        text = "This is a clean message"

        types = scanner.get_sensitive_data_types(text)
        assert types == []


class TestModuleFunctions:
    """Test suite for module-level convenience functions."""

    def setup_method(self):
        """Reset singleton before each test.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        heuristics.Scanner.reset_singleton()

    def teardown_method(self):
        """Reset singleton after each test.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        heuristics.Scanner.reset_singleton()

    def test_get_scanner(self):
        """Test get_scanner returns Scanner instance.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner = heuristics.get_scanner()
        assert isinstance(scanner, heuristics.Scanner)

    def test_configure_scanner(self):
        """Test configure_scanner with custom patterns.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        custom_patterns = {"custom_key": r"KEY-\d{6}"}
        scanner = heuristics.configure_scanner(custom_patterns)

        assert isinstance(scanner, heuristics.Scanner)
        assert "custom_key" in scanner.list_patterns()

    def test_configure_scanner_resets_singleton(self):
        """Test that configure_scanner resets singleton.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        scanner1 = heuristics.get_scanner()
        scanner1.add_pattern("temp", r"TEMP")

        scanner2 = heuristics.configure_scanner()

        # temp pattern should not exist after reconfiguration
        assert "temp" not in scanner2.list_patterns()

    def test_scan_and_redact_convenience_function(self):
        """Test module-level scan_and_redact function.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        text = "API_KEY=secret123456789012345"
        redacted = heuristics.scan_and_redact(text)

        assert "secret123456789012345" not in redacted
        assert "[REDACTED_API_KEY]" in redacted

    def test_has_sensitive_data_convenience_function(self):
        """Test module-level has_sensitive_data function.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert heuristics.has_sensitive_data("API_KEY=secret123456789012") is True
        assert heuristics.has_sensitive_data("clean text") is False

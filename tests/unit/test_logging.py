# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.logging module."""

import logging

from unittest.mock import patch

from asyncplatform import heuristics
from asyncplatform import logging as app_logging
from asyncplatform import metadata


class TestLoggingConstants:
    """Test suite for logging level constants."""

    def test_notset_constant(self):
        """Test NOTSET constant value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert app_logging.NOTSET == logging.NOTSET

    def test_trace_constant(self):
        """Test TRACE custom level constant.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert app_logging.TRACE == 5
        assert logging.TRACE == 5

    def test_debug_constant(self):
        """Test DEBUG constant value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert app_logging.DEBUG == logging.DEBUG

    def test_info_constant(self):
        """Test INFO constant value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert app_logging.INFO == logging.INFO

    def test_warning_constant(self):
        """Test WARNING constant value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert app_logging.WARNING == logging.WARNING

    def test_error_constant(self):
        """Test ERROR constant value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert app_logging.ERROR == logging.ERROR

    def test_critical_constant(self):
        """Test CRITICAL constant value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert app_logging.CRITICAL == logging.CRITICAL

    def test_fatal_constant(self):
        """Test FATAL custom level constant.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert app_logging.FATAL == 90
        assert logging.FATAL == 90

    def test_none_constant(self):
        """Test NONE custom level constant.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert app_logging.NONE == logging.FATAL + 10
        assert logging.NONE == 100


class TestGetLogger:
    """Test suite for get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test get_logger returns a Logger instance.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        logger = app_logging.get_logger()
        assert isinstance(logger, logging.Logger)

    def test_get_logger_returns_correct_name(self):
        """Test get_logger returns logger with correct name.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        logger = app_logging.get_logger()
        assert logger.name == metadata.name


class TestLogFunction:
    """Test suite for log function."""

    def setup_method(self):
        """Setup test logger.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.logger = app_logging.get_logger()
        self.original_level = self.logger.level
        self.logger.setLevel(logging.DEBUG)

    def teardown_method(self):
        """Restore logger level.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.logger.setLevel(self.original_level)

    def test_log_writes_message(self):
        """Test log function writes message.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        with patch.object(self.logger, "log") as mock_log:
            app_logging.log(logging.INFO, "test message")
            mock_log.assert_called_once_with(logging.INFO, "test message")


class TestConvenienceFunctions:
    """Test suite for convenience logging functions."""

    def setup_method(self):
        """Setup test logger.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.logger = app_logging.get_logger()
        self.original_level = self.logger.level
        self.logger.setLevel(logging.DEBUG)

    def teardown_method(self):
        """Restore logger level.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.logger.setLevel(self.original_level)

    def test_debug_function(self):
        """Test debug convenience function.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        with patch.object(self.logger, "log") as mock_log:
            app_logging.debug("debug message")
            mock_log.assert_called_once_with(logging.DEBUG, "debug message")

    def test_info_function(self):
        """Test info convenience function.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        with patch.object(self.logger, "log") as mock_log:
            app_logging.info("info message")
            mock_log.assert_called_once_with(logging.INFO, "info message")

    def test_warning_function(self):
        """Test warning convenience function.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        with patch.object(self.logger, "log") as mock_log:
            app_logging.warning("warning message")
            mock_log.assert_called_once_with(logging.WARNING, "warning message")

    def test_error_function(self):
        """Test error convenience function.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        with patch.object(self.logger, "log") as mock_log:
            app_logging.error("error message")
            mock_log.assert_called_once_with(logging.ERROR, "error message")

    def test_critical_function(self):
        """Test critical convenience function.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        with patch.object(self.logger, "log") as mock_log:
            app_logging.critical("critical message")
            mock_log.assert_called_once_with(logging.CRITICAL, "critical message")


class TestTraceFunction:
    """Test suite for trace function."""

    def setup_method(self):
        """Setup test logger.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.logger = app_logging.get_logger()
        self.original_level = self.logger.level
        self.logger.setLevel(logging.TRACE)

    def teardown_method(self):
        """Restore logger level.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.logger.setLevel(self.original_level)

    def test_trace_logs_function_name(self):
        """Test trace decorator logs function invocation.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """

        @app_logging.trace
        def test_function():
            pass

        with patch.object(self.logger, "log") as mock_log:
            test_function()
            # Should be called twice: once for entry, once for exit
            assert mock_log.call_count == 2
            # Check first call (entry)
            entry_args = mock_log.call_args_list[0][0]
            assert entry_args[0] == logging.TRACE
            assert "→" in entry_args[1]
            assert "test_function" in entry_args[1]
            # Check second call (exit)
            exit_args = mock_log.call_args_list[1][0]
            assert exit_args[0] == logging.TRACE
            assert "←" in exit_args[1]
            assert "test_function" in exit_args[1]


class TestExceptionFunction:
    """Test suite for exception function."""

    def setup_method(self):
        """Setup test logger.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.logger = app_logging.get_logger()
        self.original_level = self.logger.level
        self.logger.setLevel(logging.ERROR)

    def teardown_method(self):
        """Restore logger level.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.logger.setLevel(self.original_level)

    def test_exception_logs_exception(self):
        """Test exception function logs exception traceback.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        try:
            msg = "test error"
            raise ValueError(msg)
        except ValueError as exc:
            with patch.object(self.logger, "log") as mock_log:
                app_logging.exception(exc)
                mock_log.assert_called_once()
                args = mock_log.call_args[0]
                assert args[0] == logging.ERROR
                assert "ValueError" in args[1]
                assert "test error" in args[1]


class TestFatalFunction:
    """Test suite for fatal function."""

    def test_fatal_exits_with_code_1(self):
        """Test fatal function exits with code 1.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        with patch("sys.exit") as mock_exit:
            with patch("builtins.print") as mock_print:
                app_logging.fatal("fatal error")
                mock_exit.assert_called_once_with(1)
                mock_print.assert_called_once()
                assert "ERROR" in mock_print.call_args[0][0]
                assert "fatal error" in mock_print.call_args[0][0]


class TestSetLevel:
    """Test suite for set_level function."""

    def setup_method(self):
        """Setup test logger.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.logger = app_logging.get_logger()
        self.original_level = self.logger.level

    def teardown_method(self):
        """Restore logger level.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.logger.setLevel(self.original_level)

    def test_set_level_changes_logger_level(self):
        """Test set_level changes logger level.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        app_logging.set_level(logging.WARNING)
        assert self.logger.level == logging.WARNING

    def test_set_level_with_none_string(self):
        """Test set_level with NONE string sets to NONE level.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        app_logging.set_level("NONE")
        assert self.logger.level == app_logging.NONE

    def test_set_level_disables_propagation(self):
        """Test set_level disables propagation.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        app_logging.set_level(logging.INFO)
        assert self.logger.propagate is False

    def test_set_level_without_propagate(self):
        """Test set_level without propagate parameter.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        app_logging.set_level(logging.INFO, propagate=False)
        # Should not raise exception
        assert self.logger.level == logging.INFO


class TestSensitiveDataFiltering:
    """Test suite for sensitive data filtering functions."""

    def test_enable_sensitive_data_filtering(self):
        """Test enable_sensitive_data_filtering sets flag.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        app_logging.enable_sensitive_data_filtering()
        assert app_logging.is_sensitive_data_filtering_enabled() is True

    def test_disable_sensitive_data_filtering(self):
        """Test disable_sensitive_data_filtering clears flag.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        app_logging.enable_sensitive_data_filtering()
        app_logging.disable_sensitive_data_filtering()
        assert app_logging.is_sensitive_data_filtering_enabled() is False

    def test_is_sensitive_data_filtering_enabled_returns_bool(self):
        """Test is_sensitive_data_filtering_enabled returns boolean.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        result = app_logging.is_sensitive_data_filtering_enabled()
        assert isinstance(result, bool)

    def test_is_sensitive_data_filtering_enabled_after_enable(self):
        """Test is_sensitive_data_filtering_enabled returns True after enabling.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        app_logging.enable_sensitive_data_filtering()
        assert app_logging.is_sensitive_data_filtering_enabled() is True
        app_logging.disable_sensitive_data_filtering()

    def test_is_sensitive_data_filtering_enabled_after_disable(self):
        """Test is_sensitive_data_filtering_enabled returns False after disabling.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        app_logging.disable_sensitive_data_filtering()
        assert app_logging.is_sensitive_data_filtering_enabled() is False

    def test_log_with_sensitive_data_filtering_enabled(self):
        """Test that log messages are filtered when filtering is enabled.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        app_logging.enable_sensitive_data_filtering()

        # Mock the scan_and_redact function to verify it's called
        with patch.object(heuristics, "scan_and_redact") as mock_redact:
            mock_redact.return_value = "[REDACTED]"

            app_logging.log(app_logging.INFO, "password=secret123")

            # Verify scan_and_redact was called
            mock_redact.assert_called_once_with("password=secret123")

        # Clean up
        app_logging.disable_sensitive_data_filtering()

    def test_log_without_sensitive_data_filtering(self):
        """Test that log messages are not filtered when filtering is disabled.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        app_logging.disable_sensitive_data_filtering()

        # Mock the scan_and_redact function to verify it's NOT called
        with patch.object(heuristics, "scan_and_redact") as mock_redact:
            app_logging.log(app_logging.INFO, "test message")

            # Verify scan_and_redact was NOT called
            mock_redact.assert_not_called()


class TestSensitiveDataPatterns:
    """Test suite for sensitive data pattern management."""

    def setup_method(self):
        """Reset scanner before each test.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        heuristics.Scanner.reset_singleton()

    def teardown_method(self):
        """Reset scanner after each test.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        heuristics.Scanner.reset_singleton()

    def test_configure_sensitive_data_patterns(self):
        """Test configure_sensitive_data_patterns with custom patterns.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        custom_patterns = {"test_key": r"TEST-\d{6}"}
        app_logging.configure_sensitive_data_patterns(custom_patterns)

        patterns = app_logging.get_sensitive_data_patterns()
        assert "test_key" in patterns

    def test_get_sensitive_data_patterns(self):
        """Test get_sensitive_data_patterns returns list.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        patterns = app_logging.get_sensitive_data_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_add_sensitive_data_pattern(self):
        """Test add_sensitive_data_pattern adds new pattern.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        app_logging.add_sensitive_data_pattern("custom_pattern", r"CUSTOM-\d+")
        patterns = app_logging.get_sensitive_data_patterns()
        assert "custom_pattern" in patterns

    def test_remove_sensitive_data_pattern(self):
        """Test remove_sensitive_data_pattern removes pattern.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        app_logging.add_sensitive_data_pattern("temp_pattern", r"TEMP-\d+")
        result = app_logging.remove_sensitive_data_pattern("temp_pattern")
        assert result is True

        patterns = app_logging.get_sensitive_data_patterns()
        assert "temp_pattern" not in patterns

    def test_remove_nonexistent_pattern(self):
        """Test removing nonexistent pattern returns False.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        result = app_logging.remove_sensitive_data_pattern("nonexistent")
        assert result is False


class TestInitialize:
    """Test suite for initialize function."""

    def test_initialize_sets_up_handlers(self):
        """Test initialize sets up logging handlers.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Call initialize
        app_logging.initialize()

        # Check that logger has handlers
        logger = app_logging.get_logger()
        assert len(logger.handlers) > 0

    def test_initialize_sets_none_level(self):
        """Test initialize sets level to NONE.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        app_logging.initialize()
        logger = app_logging.get_logger()
        assert logger.level == app_logging.NONE

    def test_initialize_disables_propagation(self):
        """Test initialize disables propagation.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        app_logging.initialize()
        logger = app_logging.get_logger()
        assert logger.propagate is False


class TestGetLoggers:
    """Test suite for _get_loggers internal function."""

    def test_get_loggers_returns_set(self):
        """Test _get_loggers returns a set of loggers.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        loggers = app_logging._get_loggers()
        assert isinstance(loggers, set)

    def test_get_loggers_includes_asyncplatform_logger(self):
        """Test _get_loggers includes asyncplatform logger.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        loggers = app_logging._get_loggers()
        logger_names = {logger.name for logger in loggers}
        assert any(metadata.name in name for name in logger_names)


class TestLoggingMessageFormat:
    """Test suite for logging message format."""

    def test_logging_message_format_is_defined(self):
        """Test logging_message_format constant is defined.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert hasattr(app_logging, "logging_message_format")
        format_string = app_logging.logging_message_format
        assert "asctime" in format_string
        assert "levelname" in format_string
        assert "message" in format_string


class TestTraceDecoratorAsync:
    """Test suite for trace decorator with async functions."""

    def test_trace_async_function_with_exception(self):
        """Test trace decorator logs async function exception.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import asyncio

        import pytest

        @app_logging.trace
        async def async_function_that_raises():
            raise ValueError("Test exception")

        # Enable TRACE level to see trace messages
        app_logging.set_level(app_logging.TRACE)

        with patch.object(app_logging, "log") as mock_log:
            with pytest.raises(ValueError):
                asyncio.run(async_function_that_raises())

            # Should have logged entry, but exception message should be there
            calls = [str(call) for call in mock_log.call_args_list]
            assert any("→" in str(call) for call in calls)
            assert any("exception" in str(call).lower() for call in calls)

    def test_trace_async_function_success(self):
        """Test trace decorator logs async function success.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import asyncio

        @app_logging.trace
        async def async_function_success():
            return "success"

        # Enable TRACE level
        app_logging.set_level(app_logging.TRACE)

        with patch.object(app_logging, "log") as mock_log:
            result = asyncio.run(async_function_success())
            assert result == "success"

            # Should have logged entry and exit
            calls = [str(call) for call in mock_log.call_args_list]
            assert any("→" in str(call) for call in calls)
            assert any("←" in str(call) for call in calls)


class TestTraceDecoratorSync:
    """Test suite for trace decorator with sync functions."""

    def test_trace_sync_function_with_exception(self):
        """Test trace decorator logs sync function exception.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import pytest

        @app_logging.trace
        def sync_function_that_raises():
            raise ValueError("Test exception")

        # Enable TRACE level
        app_logging.set_level(app_logging.TRACE)

        with patch.object(app_logging, "log") as mock_log:
            with pytest.raises(ValueError):
                sync_function_that_raises()

            # Should have logged entry and exception
            calls = [str(call) for call in mock_log.call_args_list]
            assert any("→" in str(call) for call in calls)
            assert any("exception" in str(call).lower() for call in calls)

    def test_trace_sync_function_success(self):
        """Test trace decorator logs sync function success.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """

        @app_logging.trace
        def sync_function_success():
            return "success"

        # Enable TRACE level
        app_logging.set_level(app_logging.TRACE)

        with patch.object(app_logging, "log") as mock_log:
            result = sync_function_success()
            assert result == "success"

            # Should have logged entry and exit
            calls = [str(call) for call in mock_log.call_args_list]
            assert any("→" in str(call) for call in calls)
            assert any("←" in str(call) for call in calls)


class TestSetLevelAdvanced:
    """Test suite for advanced set_level functionality."""

    def test_set_level_with_invalid_string(self):
        """Test set_level raises TypeError for invalid string levels.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        import pytest

        with pytest.raises(TypeError) as exc_info:
            app_logging.set_level("INVALID")

        assert "Invalid level string" in str(exc_info.value)
        assert "INVALID" in str(exc_info.value)

    def test_set_level_with_propagate_true(self):
        """Test set_level with propagate=True sets level for all loggers.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Set level with propagate=True
        app_logging.set_level(app_logging.DEBUG, propagate=True)

        # Get all loggers
        loggers = app_logging._get_loggers()

        # Verify all loggers have DEBUG level or lower
        for logger in loggers:
            assert logger.level <= app_logging.DEBUG

    def test_set_level_propagate_clears_cache(self):
        """Test set_level with propagate=True clears the logger cache.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Call _get_loggers to populate cache
        app_logging._get_loggers()

        # Mock cache_clear to verify it's called
        with patch.object(app_logging._get_loggers, "cache_clear") as mock_clear:
            app_logging.set_level(app_logging.INFO, propagate=True)
            mock_clear.assert_called_once()

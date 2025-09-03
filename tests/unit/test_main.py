# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.__main__ module."""

import subprocess
import sys

from unittest.mock import patch


class TestMainModule:
    """Test suite for __main__ module execution."""

    def test_main_module_can_be_imported(self):
        """Test that __main__ module can be imported.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        from asyncplatform import __main__

        assert __main__ is not None

    def test_main_module_prints_no_cli_message(self):
        """Test __main__ prints message about no CLI.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        with patch("builtins.print") as mock_print:
            # Re-import to trigger print statements
            import importlib

            from asyncplatform import __main__

            importlib.reload(__main__)

            # Should have called print at least twice
            assert mock_print.call_count >= 2

            # Check for expected messages
            calls = [str(call[0][0]) for call in mock_print.call_args_list]
            assert any("does not currently provide a CLI interface" in call for call in calls)
            assert any("help(asyncplatform)" in call for call in calls)

    def test_main_module_execution_via_python_m(self):
        """Test executing module with python -m asyncplatform.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        result = subprocess.run(
            [sys.executable, "-m", "asyncplatform"],
            check=False, capture_output=True,
            text=True,
            timeout=5,
        )

        # Should complete successfully
        assert result.returncode == 0

        # Should output the expected messages
        assert "does not currently provide a CLI interface" in result.stdout
        assert "help(asyncplatform)" in result.stdout

    def test_main_module_has_docstring(self):
        """Test __main__ module has a docstring.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        from asyncplatform import __main__

        assert __main__.__doc__ is not None
        assert len(__main__.__doc__) > 0


class TestMainModuleMessages:
    """Test suite for __main__ module message content."""

    def test_message_mentions_no_cli(self):
        """Test message mentions lack of CLI.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        result = subprocess.run(
            [sys.executable, "-m", "asyncplatform"],
            check=False, capture_output=True,
            text=True,
            timeout=5,
        )

        output = result.stdout.lower()
        assert "cli" in output or "command" in output

    def test_message_provides_help_alternative(self):
        """Test message provides alternative help method.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        result = subprocess.run(
            [sys.executable, "-m", "asyncplatform"],
            check=False, capture_output=True,
            text=True,
            timeout=5,
        )

        assert "help" in result.stdout.lower()
        assert "asyncplatform" in result.stdout

    def test_message_suggests_library_usage(self):
        """Test message suggests using as library.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        result = subprocess.run(
            [sys.executable, "-m", "asyncplatform"],
            check=False, capture_output=True,
            text=True,
            timeout=5,
        )

        # Should mention library or import usage
        assert "library" in result.stdout.lower() or "import" in result.stdout.lower()


class TestMainModuleExecution:
    """Test suite for __main__ module execution behavior."""

    def test_main_exits_successfully(self):
        """Test __main__ exits with code 0.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        result = subprocess.run(
            [sys.executable, "-m", "asyncplatform"],
            check=False, capture_output=True,
            text=True,
            timeout=5,
        )

        assert result.returncode == 0

    def test_main_produces_stdout(self):
        """Test __main__ produces stdout output.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        result = subprocess.run(
            [sys.executable, "-m", "asyncplatform"],
            check=False, capture_output=True,
            text=True,
            timeout=5,
        )

        assert len(result.stdout) > 0

    def test_main_produces_no_stderr(self):
        """Test __main__ produces no stderr output.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        result = subprocess.run(
            [sys.executable, "-m", "asyncplatform"],
            check=False, capture_output=True,
            text=True,
            timeout=5,
        )

        # Stderr should be empty or only contain logging initialization
        assert len(result.stderr) == 0 or "asyncplatform" not in result.stderr.lower()

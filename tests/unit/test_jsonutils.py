# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.jsonutils module."""

import json

from unittest.mock import patch

import pytest

from asyncplatform import exceptions
from asyncplatform import jsonutils


class TestLoads:
    """Test suite for jsonutils.loads function."""

    def test_loads_valid_dict(self):
        """Test loading valid JSON dict string.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_str = '{"key": "value", "number": 42}'
        result = jsonutils.loads(json_str)

        assert isinstance(result, dict)
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_loads_valid_list(self):
        """Test loading valid JSON list string.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_str = '[1, 2, 3, "four"]'
        result = jsonutils.loads(json_str)

        assert isinstance(result, list)
        assert len(result) == 4
        assert result[3] == "four"

    def test_loads_nested_structure(self):
        """Test loading nested JSON structure.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_str = (
            '{"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}'
        )
        result = jsonutils.loads(json_str)

        assert isinstance(result, dict)
        assert "users" in result
        assert len(result["users"]) == 2
        assert result["users"][0]["name"] == "Alice"

    def test_loads_empty_dict(self):
        """Test loading empty JSON dict.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_str = "{}"
        result = jsonutils.loads(json_str)

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_loads_empty_list(self):
        """Test loading empty JSON list.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_str = "[]"
        result = jsonutils.loads(json_str)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_loads_with_unicode(self):
        """Test loading JSON with unicode characters.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_str = '{"message": "Hello 世界 🌍"}'
        result = jsonutils.loads(json_str)

        assert result["message"] == "Hello 世界 🌍"

    def test_loads_invalid_json_raises_serialization_error(self):
        """Test that invalid JSON raises SerializationError.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        invalid_json = "{invalid json}"

        with pytest.raises(exceptions.SerializationError) as exc_info:
            jsonutils.loads(invalid_json)

        assert "Failed to parse JSON" in str(exc_info.value)

    def test_loads_incomplete_json_raises_error(self):
        """Test that incomplete JSON raises SerializationError.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        incomplete_json = '{"key": "value"'

        with pytest.raises(exceptions.SerializationError) as exc_info:
            jsonutils.loads(incomplete_json)

        assert "Failed to parse JSON" in str(exc_info.value)

    def test_loads_none_input_raises_error(self):
        """Test that None input raises SerializationError.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        with pytest.raises(exceptions.SerializationError) as exc_info:
            jsonutils.loads(None)

        assert "Unexpected error parsing JSON" in str(exc_info.value)

    def test_loads_error_with_long_input(self):
        """Test that error is raised with long input data.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Create an invalid JSON string longer than 200 characters
        long_json = '{"data": invalid' + "x" * 300 + "}"

        with pytest.raises(exceptions.SerializationError) as exc_info:
            jsonutils.loads(long_json)

        # Should raise SerializationError
        assert "Failed to parse JSON" in str(exc_info.value)

    def test_loads_with_special_types(self):
        """Test loading JSON with null, boolean values.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_str = '{"null_value": null, "bool_true": true, "bool_false": false}'
        result = jsonutils.loads(json_str)

        assert result["null_value"] is None
        assert result["bool_true"] is True
        assert result["bool_false"] is False


class TestDumps:
    """Test suite for jsonutils.dumps function."""

    def test_dumps_dict(self):
        """Test dumping dict to JSON string.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = {"key": "value", "number": 42}
        result = jsonutils.dumps(data)

        assert isinstance(result, str)
        # Verify it's valid JSON by parsing it back
        parsed = json.loads(result)
        assert parsed == data

    def test_dumps_list(self):
        """Test dumping list to JSON string.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = [1, 2, 3, "four"]
        result = jsonutils.dumps(data)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == data

    def test_dumps_nested_structure(self):
        """Test dumping nested structure to JSON.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}
        result = jsonutils.dumps(data)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == data

    def test_dumps_empty_dict(self):
        """Test dumping empty dict.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = {}
        result = jsonutils.dumps(data)

        assert result == "{}"

    def test_dumps_empty_list(self):
        """Test dumping empty list.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = []
        result = jsonutils.dumps(data)

        assert result == "[]"

    def test_dumps_with_unicode(self):
        """Test dumping data with unicode characters.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = {"message": "Hello 世界 🌍"}
        result = jsonutils.dumps(data)

        parsed = json.loads(result)
        assert parsed["message"] == "Hello 世界 🌍"

    def test_dumps_with_special_types(self):
        """Test dumping data with None and boolean values.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = {"null_value": None, "bool_true": True, "bool_false": False}
        result = jsonutils.dumps(data)

        parsed = json.loads(result)
        assert parsed["null_value"] is None
        assert parsed["bool_true"] is True
        assert parsed["bool_false"] is False

    def test_dumps_non_serializable_raises_error(self):
        """Test that non-serializable object raises SerializationError.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """

        class NonSerializable:
            pass

        data = {"obj": NonSerializable()}

        with pytest.raises(exceptions.SerializationError) as exc_info:
            jsonutils.dumps(data)

        assert "Failed to serialize object to JSON" in str(exc_info.value)

    def test_dumps_circular_reference_raises_error(self):
        """Test that circular reference raises SerializationError.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = {"key": "value"}
        data["self"] = data  # Create circular reference

        with pytest.raises(exceptions.SerializationError) as exc_info:
            jsonutils.dumps(data)

        assert "Failed to serialize object to JSON" in str(exc_info.value)

    @patch("json.dumps")
    def test_dumps_unexpected_exception_raises_error(self, mock_dumps):
        """Test that unexpected exception in dumps raises SerializationError.

        Args:
            mock_dumps: Mock for json.dumps

        Returns:
            None

        Raises:
            None
        """
        # Make json.dumps raise an unexpected exception
        mock_dumps.side_effect = RuntimeError("Unexpected error")

        data = {"key": "value"}

        with pytest.raises(exceptions.SerializationError) as exc_info:
            jsonutils.dumps(data)

        assert "Unexpected error serializing JSON" in str(exc_info.value)


class TestRoundTrip:
    """Test suite for round-trip JSON operations."""

    def test_roundtrip_dict(self):
        """Test dumps followed by loads returns original dict.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        original = {"key": "value", "number": 42, "nested": {"inner": "data"}}

        json_str = jsonutils.dumps(original)
        result = jsonutils.loads(json_str)

        assert result == original

    def test_roundtrip_list(self):
        """Test dumps followed by loads returns original list.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        original = [1, 2, 3, {"key": "value"}, [4, 5, 6]]

        json_str = jsonutils.dumps(original)
        result = jsonutils.loads(json_str)

        assert result == original

    def test_roundtrip_complex_structure(self):
        """Test round-trip with complex nested structure.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        original = {
            "users": [{"name": "Alice", "age": 30, "active": True, "notes": None}],
            "count": 1,
            "metadata": {"version": "1.0", "tags": ["test", "demo"]},
        }

        json_str = jsonutils.dumps(original)
        result = jsonutils.loads(json_str)

        assert result == original


class TestErrorHandling:
    """Test suite for error handling in jsonutils."""

    def test_loads_raises_serialization_error(self):
        """Test that SerializationError is raised for invalid JSON.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        invalid_json = '{"key": invalid}'

        with pytest.raises(exceptions.SerializationError) as exc_info:
            jsonutils.loads(invalid_json)

        error = exc_info.value
        assert "Failed to parse JSON" in str(error)
        assert error.message is not None

    def test_dumps_raises_serialization_error(self):
        """Test that SerializationError is raised for non-serializable objects.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """

        class CustomObject:
            pass

        with pytest.raises(exceptions.SerializationError) as exc_info:
            jsonutils.dumps({"obj": CustomObject()})

        error = exc_info.value
        assert "Failed to serialize object to JSON" in str(error)
        assert error.message is not None

    def test_loads_stores_original_exception(self):
        """Test that SerializationError stores original exception.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        invalid_json = '{"bad": json}'

        with pytest.raises(exceptions.SerializationError) as exc_info:
            jsonutils.loads(invalid_json)

        # Check that the original exception is stored
        assert exc_info.value._exc is not None
        assert isinstance(exc_info.value._exc, json.JSONDecodeError)

    def test_dumps_stores_original_exception(self):
        """Test that SerializationError stores original exception.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """

        class NonSerializable:
            pass

        with pytest.raises(exceptions.SerializationError) as exc_info:
            jsonutils.dumps({"obj": NonSerializable()})

        # Check that the original exception is stored
        assert exc_info.value._exc is not None
        assert isinstance(exc_info.value._exc, TypeError)


class TestLoadsNumericTypes:
    """Test suite for numeric type handling in loads."""

    def test_loads_integers(self):
        """Test loading integers of various sizes.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_str = '{"small": 0, "positive": 42, "negative": -100, "large": 9999999999}'
        result = jsonutils.loads(json_str)

        assert result["small"] == 0
        assert result["positive"] == 42
        assert result["negative"] == -100
        assert result["large"] == 9999999999

    def test_loads_floats(self):
        """Test loading floating point numbers.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_str = '{"decimal": 3.14, "negative": -2.5, "zero": 0.0}'
        result = jsonutils.loads(json_str)

        assert result["decimal"] == 3.14
        assert result["negative"] == -2.5
        assert result["zero"] == 0.0

    def test_loads_scientific_notation(self):
        """Test loading numbers in scientific notation.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_str = '{"sci": 1.23e10, "neg_exp": 4.56e-5}'
        result = jsonutils.loads(json_str)

        assert result["sci"] == 1.23e10
        assert result["neg_exp"] == 4.56e-5

    def test_loads_mixed_number_types(self):
        """Test loading list with mixed numeric types.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_str = "[0, 1, -1, 3.14, -2.5, 1e10]"
        result = jsonutils.loads(json_str)

        assert len(result) == 6
        assert isinstance(result[0], int)
        assert isinstance(result[3], float)


class TestLoadsEdgeCases:
    """Test suite for edge cases in loads."""

    def test_loads_with_whitespace(self):
        """Test loading JSON with extra whitespace.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_str = '  \n\t  {  "key"  :  "value"  }  \n  '
        result = jsonutils.loads(json_str)

        assert result == {"key": "value"}

    def test_loads_escaped_characters(self):
        """Test loading JSON with escaped characters.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_str = r'{"quote": "He said \"hello\"", "newline": "Line1\nLine2", "tab": "Col1\tCol2"}'
        result = jsonutils.loads(json_str)

        assert result["quote"] == 'He said "hello"'
        assert result["newline"] == "Line1\nLine2"
        assert result["tab"] == "Col1\tCol2"

    def test_loads_empty_string_raises_error(self):
        """Test that empty string raises SerializationError.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        with pytest.raises(exceptions.SerializationError):
            jsonutils.loads("")

    def test_loads_only_whitespace_raises_error(self):
        """Test that whitespace-only string raises SerializationError.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        with pytest.raises(exceptions.SerializationError):
            jsonutils.loads("   \n\t   ")

    def test_loads_single_value(self):
        """Test loading single JSON values.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # JSON standard allows top-level primitives
        assert jsonutils.loads('"string"') == "string"
        assert jsonutils.loads("42") == 42
        assert jsonutils.loads("true") is True
        assert jsonutils.loads("false") is False
        assert jsonutils.loads("null") is None

    def test_loads_deeply_nested(self):
        """Test loading deeply nested JSON structure.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Create a deeply nested structure
        nested = '{"a": {"b": {"c": {"d": {"e": {"f": "deep"}}}}}}'
        result = jsonutils.loads(nested)

        assert result["a"]["b"]["c"]["d"]["e"]["f"] == "deep"

    def test_loads_with_duplicate_keys(self):
        """Test loading JSON with duplicate keys (last value wins).

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_str = '{"key": "first", "key": "second"}'
        result = jsonutils.loads(json_str)

        # JSON spec allows this, last value wins
        assert result["key"] == "second"

    def test_loads_bytes_input_works(self):
        """Test that bytes input is accepted (Python 3 behavior).

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # json.loads accepts bytes in Python 3
        result = jsonutils.loads(b'{"key": "value"}')
        assert result == {"key": "value"}


class TestDumpsNumericTypes:
    """Test suite for numeric type handling in dumps."""

    def test_dumps_integers(self):
        """Test dumping integers of various sizes.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = {"small": 0, "positive": 42, "negative": -100, "large": 9999999999}
        result = jsonutils.dumps(data)

        parsed = json.loads(result)
        assert parsed == data

    def test_dumps_floats(self):
        """Test dumping floating point numbers.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = {"decimal": 3.14, "negative": -2.5, "zero": 0.0}
        result = jsonutils.dumps(data)

        parsed = json.loads(result)
        assert parsed == data

    def test_dumps_mixed_list(self):
        """Test dumping list with mixed types.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = [1, "string", 3.14, True, None, {"nested": "dict"}]
        result = jsonutils.dumps(data)

        parsed = json.loads(result)
        assert parsed == data


class TestDumpsEdgeCases:
    """Test suite for edge cases in dumps."""

    def test_dumps_string_with_special_characters(self):
        """Test dumping strings with special characters.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = {
            "quote": 'He said "hello"',
            "newline": "Line1\nLine2",
            "tab": "Col1\tCol2",
            "backslash": "Path\\to\\file",
        }
        result = jsonutils.dumps(data)

        parsed = json.loads(result)
        assert parsed == data

    def test_dumps_deeply_nested(self):
        """Test dumping deeply nested structure.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = {"a": {"b": {"c": {"d": {"e": {"f": "deep"}}}}}}
        result = jsonutils.dumps(data)

        parsed = json.loads(result)
        assert parsed == data

    def test_dumps_large_list(self):
        """Test dumping large list.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = list(range(1000))
        result = jsonutils.dumps(data)

        parsed = json.loads(result)
        assert parsed == data

    def test_dumps_integer_keys_converted_to_strings(self):
        """Test that integer keys are converted to strings in JSON.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Python allows integer keys, but JSON requires string keys
        data = {1: "one", 2: "two", 3: "three"}
        result = jsonutils.dumps(data)

        parsed = json.loads(result)
        # Keys become strings in JSON
        assert parsed == {"1": "one", "2": "two", "3": "three"}

    def test_dumps_function_raises_error(self):
        """Test that function object raises SerializationError.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """

        def my_function():
            pass

        with pytest.raises(exceptions.SerializationError):
            jsonutils.dumps({"func": my_function})

    def test_dumps_lambda_raises_error(self):
        """Test that lambda raises SerializationError.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        with pytest.raises(exceptions.SerializationError):
            jsonutils.dumps({"lambda": lambda x: x})

    def test_dumps_set_raises_error(self):
        """Test that set raises SerializationError.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        with pytest.raises(exceptions.SerializationError):
            jsonutils.dumps({"set": {1, 2, 3}})

    def test_dumps_tuple_becomes_list(self):
        """Test that tuple is serialized as list.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        data = {"tuple": (1, 2, 3)}
        result = jsonutils.dumps(data)

        parsed = json.loads(result)
        # Tuples become lists in JSON
        assert parsed == {"tuple": [1, 2, 3]}


class TestSpecialCases:
    """Test suite for special JSON cases."""

    def test_roundtrip_preserves_order(self):
        """Test that round-trip preserves key order (Python 3.7+).

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        original = {"z": 1, "a": 2, "m": 3}
        json_str = jsonutils.dumps(original)
        result = jsonutils.loads(json_str)

        # Python 3.7+ maintains insertion order for dicts
        assert list(result.keys()) == ["z", "a", "m"]

    def test_loads_returns_correct_type(self):
        """Test that loads returns dict or list as appropriate.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        dict_result = jsonutils.loads('{"key": "value"}')
        list_result = jsonutils.loads("[1, 2, 3]")

        assert isinstance(dict_result, dict)
        assert isinstance(list_result, list)
        assert not isinstance(dict_result, list)
        assert not isinstance(list_result, dict)

    def test_dumps_returns_string(self):
        """Test that dumps always returns string type.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        dict_result = jsonutils.dumps({"key": "value"})
        list_result = jsonutils.dumps([1, 2, 3])

        assert isinstance(dict_result, str)
        assert isinstance(list_result, str)

    def test_error_message_includes_original_exception(self):
        """Test that error messages include information from original exception.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Test loads error
        with pytest.raises(exceptions.SerializationError) as exc_info:
            jsonutils.loads('{"bad": syntax}')

        assert "Failed to parse JSON" in str(exc_info.value)

        # Test dumps error
        class BadObject:
            pass

        with pytest.raises(exceptions.SerializationError) as exc_info:
            jsonutils.dumps({"obj": BadObject()})

        assert "Failed to serialize object to JSON" in str(exc_info.value)

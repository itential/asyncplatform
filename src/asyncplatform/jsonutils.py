# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""JSON serialization utilities for the asyncplatform SDK.

This module provides wrapper functions around Python's json module with
enhanced error handling and logging for common JSON operations.
"""

from __future__ import annotations

import json

from . import exceptions
from . import logging


def loads(s: str) -> dict | list:
    """Convert a JSON formatted string to a dict or list object.

    Args:
        s: The JSON object represented as a string

    Returns:
        Parsed JSON data as a dictionary or list

    Raises:
        SerializationError: If the string cannot be parsed as JSON
    """
    try:
        return json.loads(s)

    except json.JSONDecodeError as exc:
        logging.exception(exc)
        msg = f"Failed to parse JSON: {exc!s}"
        raise exceptions.SerializationError(msg, exc=exc) from exc

    except Exception as exc:
        logging.exception(exc)
        msg = f"Unexpected error parsing JSON: {exc!s}"
        raise exceptions.SerializationError(msg, exc=exc) from exc


def dumps(o: dict | list) -> str:
    """Convert a dict or list to a JSON string.

    Args:
        o: The list or dict object to dump to a string

    Returns:
        JSON string representation of the input object

    Raises:
        SerializationError: If the object cannot be serialized to JSON
    """
    try:
        return json.dumps(o)

    except (TypeError, ValueError) as exc:
        logging.exception(exc)
        msg = f"Failed to serialize object to JSON: {exc!s}"
        raise exceptions.SerializationError(msg, exc=exc) from exc

    except Exception as exc:
        logging.exception(exc)
        msg = f"Unexpected error serializing JSON: {exc!s}"
        raise exceptions.SerializationError(msg, exc=exc) from exc

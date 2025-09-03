# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Async Python client library for the Itential Platform REST API.

This package provides a high-level interface for interacting with Itential
automation platform services, specifically designed for asynchronous operations.

Example:
    Basic usage with async context manager::

        import asyncplatform

        cfg = {
            "host": "platform.example.com",
            "user": "admin@domain",
            "password": "secure_password"
        }

        async with asyncplatform.client(**cfg) as client:
            projects = await client.automation_studio.get_projects()
"""

from __future__ import annotations

from . import logging
from . import metadata
from .client import Client as client

__version__ = metadata.version

__all__ = ("client", "logging")

logging.initialize()

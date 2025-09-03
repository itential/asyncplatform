# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Package metadata and version information.

This module provides access to package metadata including name, author,
and version information extracted from the package distribution.
"""

from __future__ import annotations

from importlib.metadata import version as _version

name: str = "asyncplatform"
author: str = "Itential"
version: str = _version(name)

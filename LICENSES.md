# Third-Party Licenses

This file contains information about the licenses of third-party dependencies used in asyncplatform.

## asyncplatform License

asyncplatform is licensed under the GNU General Public License v3.0 or later (GPL-3.0-or-later).

- **Copyright**: Copyright (c) 2025 Itential, Inc
- **License**: GPL-3.0-or-later
- **License Text**: See [LICENSE](LICENSE) file in the root directory

---

## Runtime Dependencies

The following dependencies are required for asyncplatform to run:

### ipsdk

- **Purpose**: Core SDK for interacting with the Itential Platform
- **Homepage**: https://pypi.org/project/ipsdk/
- **License**: GPL-3.0-or-later (Compatible with asyncplatform)
- **Notes**: Maintained by Itential, Inc

---

## Transitive Dependencies

The following packages are indirect dependencies (dependencies of our direct dependencies):

### httpx

- **Purpose**: HTTP client library (dependency of ipsdk)
- **Homepage**: https://www.python-httpx.org/
- **Repository**: https://github.com/encode/httpx
- **License**: BSD 3-Clause License (GPL-compatible)
- **License Text**: https://github.com/encode/httpx/blob/master/LICENSE.md
- **Copyright**: Copyright © 2019, Encode OSS Ltd.

### httpcore

- **Purpose**: HTTP core library (dependency of httpx)
- **Homepage**: https://www.encode.io/httpcore/
- **Repository**: https://github.com/encode/httpcore
- **License**: BSD 3-Clause License (GPL-compatible)
- **License Text**: https://github.com/encode/httpcore/blob/master/LICENSE.md
- **Copyright**: Copyright © 2019, Encode OSS Ltd.

### certifi

- **Purpose**: Mozilla's CA Bundle (dependency of httpx)
- **Homepage**: https://github.com/certifi/python-certifi
- **License**: Mozilla Public License 2.0 (MPL 2.0) (GPL-compatible)
- **Notes**: Provides Mozilla's carefully curated collection of Root Certificates

### h11

- **Purpose**: Pure-Python HTTP/1.1 protocol implementation (dependency of httpcore)
- **Homepage**: https://github.com/python-hyper/h11
- **License**: MIT License (GPL-compatible)
- **Copyright**: Copyright (c) 2016 Nathaniel J. Smith

### sniffio

- **Purpose**: Sniff out which async library code is running under (dependency of httpcore)
- **Homepage**: https://github.com/python-trio/sniffio
- **License**: MIT License or Apache License 2.0 (GPL-compatible)
- **Copyright**: Copyright (c) 2018 Nathaniel J. Smith

### idna

- **Purpose**: Internationalized Domain Names in Applications (IDNA) (dependency of httpx)
- **Homepage**: https://github.com/kjd/idna
- **License**: BSD 3-Clause License (GPL-compatible)
- **Notes**: Implementation of IDNA2008 and UTS-46

### anyio

- **Purpose**: High-level async framework abstraction (dependency of httpx)
- **Homepage**: https://github.com/agronholm/anyio
- **License**: MIT License (GPL-compatible)
- **Copyright**: Copyright (c) 2018 Alex Grönholm

---

## Development Dependencies

The following dependencies are used for development, testing, and building but are not included in the distributed package:

### pytest

- **Purpose**: Testing framework
- **Homepage**: https://pytest.org/
- **License**: MIT License (GPL-compatible)

### pytest-cov

- **Purpose**: Coverage plugin for pytest
- **Homepage**: https://github.com/pytest-dev/pytest-cov
- **License**: MIT License (GPL-compatible)

### pytest-asyncio

- **Purpose**: Pytest support for asyncio
- **Homepage**: https://github.com/pytest-dev/pytest-asyncio
- **License**: Apache License 2.0 (GPL-compatible)

### ruff

- **Purpose**: Fast Python linter and formatter
- **Homepage**: https://github.com/astral-sh/ruff
- **License**: MIT License (GPL-compatible)

### mypy

- **Purpose**: Static type checker for Python
- **Homepage**: https://github.com/python/mypy
- **License**: MIT License (GPL-compatible)

### coverage

- **Purpose**: Code coverage measurement
- **Homepage**: https://github.com/nedbat/coveragepy
- **License**: Apache License 2.0 (GPL-compatible)

### build

- **Purpose**: Python package build frontend
- **Homepage**: https://github.com/pypa/build
- **License**: MIT License (GPL-compatible)

### bandit

- **Purpose**: Security linter for Python
- **Homepage**: https://github.com/PyCQA/bandit
- **License**: Apache License 2.0 (GPL-compatible)

### pre-commit

- **Purpose**: Git hook framework
- **Homepage**: https://pre-commit.com/
- **License**: MIT License (GPL-compatible)

### tox

- **Purpose**: Testing automation
- **Homepage**: https://tox.wiki/
- **License**: MIT License (GPL-compatible)

### tox-uv

- **Purpose**: Tox plugin for uv
- **Homepage**: https://github.com/tox-dev/tox-uv
- **License**: MIT License (GPL-compatible)

---

## Build System Dependencies

### hatchling

- **Purpose**: Build backend for Python packages
- **Homepage**: https://github.com/pypa/hatch/tree/master/backend
- **License**: MIT License (GPL-compatible)

### uv-dynamic-versioning

- **Purpose**: Dynamic versioning plugin for uv
- **Homepage**: https://github.com/ofek/uv-dynamic-versioning
- **License**: MIT License (GPL-compatible)

---

## License Compatibility

All dependencies listed above use licenses that are compatible with the GNU General Public License v3.0 or later:

- **BSD 3-Clause License**: GPL-compatible (permissive)
- **MIT License**: GPL-compatible (permissive)
- **Apache License 2.0**: GPL-compatible (permissive)
- **Mozilla Public License 2.0**: GPL-compatible with certain provisions

This means:
1. asyncplatform can legally use all of these dependencies
2. Users can redistribute asyncplatform under GPL-3.0-or-later terms
3. All freedom-preserving requirements of GPL are maintained

---

## How to View Installed Licenses

To view the licenses of installed packages in your environment:

```bash
# List all installed packages with their licenses
uv pip list --format=json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for p in sorted(data, key=lambda x: x['name']):
    print(f\"{p['name']}=={p['version']}\")
"

# View license information for a specific package
python3 -c "
import importlib.metadata
pkg = 'httpx'
try:
    metadata = importlib.metadata.metadata(pkg)
    print(f\"Package: {pkg}\")
    print(f\"License: {metadata.get('License', 'Not specified')}\")
except:
    print(f\"Package {pkg} not found\")
"
```

---

## Reporting License Issues

If you believe there is a license compatibility issue or if you have questions about the licensing of this project, please:

1. Open an issue at: https://github.com/itential/asyncplatform/issues
2. Contact us at: opensource@itential.com

---

## Updates to This File

This file was last updated: 2025-12-10

When dependencies are added, updated, or removed, this file should be updated accordingly to maintain accurate license attribution.

---

**Note**: This project complies with the GNU General Public License v3.0 or later. All source code files include appropriate copyright notices and SPDX license identifiers. For the complete license text, see the [LICENSE](LICENSE) file.

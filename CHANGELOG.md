# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.15.5] - 2026-02-27

- Fix: correct `concord232_server` entry point (`concord232.main:main`) so the server starts inside the add-on container.

## [0.15.4] - 2025-02-27

- Add-on: improved DOCS.md (configuration table formatting, Advantech EKI-1511L-A default port 5500). Expose only port 5007; default serial example set to rfc2217.

## [0.15.3] - 2025-02-27

- Fixed `ModuleNotFoundError: No module named 'concord232_server'` in the Home Assistant add-on by correcting the `concord232_server` entry point in pyproject.toml to use `concord232.main:main` instead of the non-existent `concord232_server` module.
- Add-on: expose port 5008 in addition to 5007 so the API is reachable when the add-on is configured to use port 5008.
- Documentation: added "Calling the concord232 API from HA (e.g. rest_command)" to the migration guide (use 127.0.0.1 and the correct port to avoid timeouts when the app runs on the same host as Home Assistant).

## Previous changes (0.15.2 and earlier)

- Migrated all CLI and codebase output from print statements to structured logging using the logging module.
- Updated CLI tests to check stderr for log output instead of stdout, ensuring compatibility with structured logging.
- Implemented test mode support in the CLI and refactored client import logic.
- Updated TODO.md to include new features and codebase improvements.
- Added partition support to the client and updated documentation.
- Added configuration file support for server settings in README and main.py.
- Enhanced development setup by adding pytest-cov to dev dependencies and updated README for coverage badge.
- Improved test coverage and added new tests for message length checks and decoding functions.
- Updated project metadata in pyproject.toml (version bump to 0.15.1, enhanced description, added dependencies).
- Revised README to improve code style, linting, formatting instructions, and included pre-commit setup details.
- Configured Black and isort for code formatting, enhanced CI workflow to include formatting checks, and marked test organization as complete in TODO.md.
- Added CLI help and error messages.
- Updated pyproject.toml to include project metadata and optional dependencies for documentation.
- Docstring improvements.
- Added automated linting with Ruff to CI and updated README with usage instructions.
- Enhanced documentation with detailed docstrings for modules, classes, and functions.
- Linted code and ensured all tests passed.
- Updated pyproject.toml to include pytest as a dev dependency, enhanced README with testing instructions, and modified setup.py to support dev dependencies.
- Added a system diagram to the documentation.
- Added CI workflow to ensure code quality and test coverage.
- Added type hints to all major source files and enabled mypy static type checking. The codebase is now fully type-annotated and mypy clean.
- Integrated gitleaks as a pre-commit hook to automatically scan for secrets and credentials in staged changes.

## [0.1.0] - YYYY-MM-DD

- Initial release.

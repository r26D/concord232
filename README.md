# GE Concord 4 RS232 Automation Module Interface Library and Server

This is a tool to let you interact with your GE Concord 4 alarm panel via
the RS232 Automation module.

The goal of this project was to utilize my GE Concord 4 alarm panel with [Home Assistant](https://home-assistant.io/)

Following the framework of [kk7ds](https://github.com/kk7ds/pynx584) to integrate the nx584 into Home Assistant, and [douglasdecouto](https://github.com/douglasdecouto/py-concord)'s work into building the base communication class as part of their integration into the Indigo platform, we now have a working Interlogix/GE Concord 4 Automation Module interface

To install::

```
sudo pip3 install concord232
```

## Installing Your Local Version

If you want to use your own improved version of this package (instead of the version from PyPI), you can install it directly from your local source.

**1. Uninstall the PyPI version (optional, but recommended):**

```sh
pip uninstall concord232
```

**2. Install your local version in "editable" mode (recommended for development):**

```sh
pip install -e .
```

This allows you to make changes to the code and have them reflected immediately.

**3. Or, install your local version as a regular package:**

```sh
pip install .
```

**4. Verify your installation:**

```sh
pip show concord232
```

Check that the `Location:` field points to your local directory.

The server must be run on a machine with connectivity to the panel, to get started, you must only supply the serial port. In this case I use a USB to Serial adapter

```
concord232_server --serial /dev/ttyUSB0
```

You can now also use a configuration file (`config.ini` by default) to specify server settings. Command-line arguments will override config file values if both are provided.

### Using a config file

Create a `config.ini` file in your project directory (or specify a different file with `--config myfile.ini`). Example:

```
[server]
# Serial port to open for stream (e.g., /dev/ttyUSB0 or COM3)
serial = /dev/ttyUSB0
# Listen address for the API server (default: 0.0.0.0, all interfaces)
listen = 0.0.0.0
# Listen port for the API server (default: 5007)
port = 5007
# Path to log file (default: none; logs to stdout if not set)
log =
```

You can then start the server with just:

```
concord232_server
```

Or specify a different config file:

```
concord232_server --config mysettings.ini
```

Any command-line argument (e.g., `--serial`, `--port`) will override the value in the config file.

Once that is running, you should be able to do something like this::

```
 $ concord232_client summary
 +------+-----------------+--------+--------+
 | Zone |       Name      | Bypass | Status |
 +------+-----------------+--------+--------+
 |  1   |    FRONT DOOR   |   -    | False  |
 |  2   |   GARAGE DOOR   |   -    | False  |
 |  3   |     SLIDING     |   -    | False  |
 |  4   | MOTION DETECTOR |   -    | False  |
 +------+-----------------+--------+--------+
```

## Basic arming and disarming

Arm to stay (level 2)

```
concord232_client arm-stay
```

Arm to away (level 3)

```
concord232_client arm-away
```

Disarm

```
concord232_client disarm --master 1234
```

## Arming with options

Both stay (level 2) and away (level 3) alarms can take one of two
options: silent arming, or instant arming. Silent arming will not
beep while the alarm is setting. Instant arming has no delay.
Clearly, this should only be used with away arming if you are already
outside.

Examples:

Arm to stay with no delay

```
concord232_client arm-stay-instant
```

Arm to away without beeps

```
concord232_client arm-away-silent
```

## Home Assistant

Home Assistant will automatically download and install the pip3 library, but it only utilizes the Client to connect to the server.

### Running the server on Home Assistant (e.g. Yellow)

To run the concord232 server **on your Home Assistant host** (e.g. Home Assistant Yellow) so it starts automatically with HA:

1. Add this repository as an app source: **Settings → Apps** → **⋮** (three dots) → **Repositories** → add `https://github.com/r26d/concord232`. (In older HA versions the menu may still be **Settings → Add-ons → Add-on store**.)
2. Install the **Concord232** app, set the **serial** option (e.g. `/dev/ttyUSB0` for a USB adapter, or `rfc2217://host:port` for network serial), then enable **Start on boot** and start the app.
3. In the [Concord Alarm](https://www.home-assistant.io/integrations/concord/) integration, use host `localhost` and port `5007` (or the port you configured).

See **[Migrating from Mac Mini to Home Assistant Yellow](docs-site/docs/migration-mac-mini-to-ha-yellow.md)** for a full step-by-step migration and troubleshooting.

### Running the server on a separate machine (e.g. Raspberry Pi, Mac)

For a server on another machine (Raspberry Pi, Mac Mini, etc.), you can use a [systemd service](http://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd/) to run the server at boot. Point the Concord Alarm integration in Home Assistant at that machine’s host and port (e.g. `5007`).

## HTTP API

The concord232 server also exposes a simple HTTP API for interacting with your panel.  
Below are the available endpoints and their usage:

| Endpoint      | Method | Description/Commands                                           |
| ------------- | ------ | -------------------------------------------------------------- |
| `/panel`      | GET    | Get panel state                                                |
| `/zones`      | GET    | Get all zones                                                  |
| `/partitions` | GET    | Get all partitions                                             |
| `/command`    | GET    | `cmd=arm`, `cmd=disarm`, `cmd=keys` (see below for parameters) |
| `/version`    | GET    | Get API version                                                |
| `/equipment`  | GET    | Request all equipment data                                     |
| `/all_data`   | GET    | Request dynamic data refresh                                   |

### `/command` endpoint

- **Arm the system:**
  - `/command?cmd=arm&level=stay&option=<option>`
  - `/command?cmd=arm&level=away&option=<option>`

- **Disarm the system:**
  - `/command?cmd=disarm&master_pin=<PIN>`

- **Send keys (e.g., \*, #, digits):**
  - `/command?cmd=keys&keys=<keys>&group=<group>`
  - Example: To send a `*` key to partition 3:  
    `/command?cmd=keys&keys=*&group=3`

### Example usage

To send a \* key to partition 3 using curl:

```sh
curl "http://<your_server_address>:<port>/command?cmd=keys&keys=*&group=3"
```

Replace `<your_server_address>` and `<port>` with your server's address and port.

## Partition Support

You can target specific partitions for arming, disarming, and sending keys using the `--partition` argument in the CLI, or the `partition` parameter in the HTTP API.

### CLI Examples

Arm partition 2 to stay:

```
concord232_client arm-stay --partition 2
```

Disarm partition 3 with master PIN:

```
concord232_client disarm --master 1234 --partition 3
```

Send keys to partition 4:

```
concord232_client keys --keys 1234* --partition 4
```

If `--partition` is not specified, partition 1 is used by default.

### HTTP API Partition Parameter

For the `/command` endpoint, you can specify the `partition` parameter for `cmd=keys` (and for custom arming/disarming via keypresses):

- **Send keys to a specific partition:**
  - `/command?cmd=keys&keys=<keys>&group=<group>&partition=<partition_number>`
  - Example: To send a `*` key to partition 3:
    `/command?cmd=keys&keys=*&group=True&partition=3`

## Testing

This project uses [pytest](https://pytest.org/) for testing and [uv](https://github.com/astral-sh/uv) as the Python package manager.

### CLI Test Mode

The CLI (`concord232_client`) supports a test mode for automated testing. If you set the environment variable `CONCORD232_TEST_MODE=1`, the CLI will use a mock client that returns fixed data and does not make any real network requests. This allows CLI tests to run reliably without requiring a running server.

Example:

```sh
CONCORD232_TEST_MODE=1 python concord232_client summary
```

This is used automatically in the CLI test suite.

To run the tests:

```sh
uv venv .venv
source .venv/bin/activate
uv pip install -e .
uv pip install pytest
pytest
```

For development, you can install all dev dependencies with:

```sh
uv pip install --system --dev
```

You can also run tests in CI using GitHub Actions (see `.github/workflows/ci.yml`).

## Code Style, Linting, and Formatting

This project uses [Ruff](https://docs.astral.sh/ruff/), [Black](https://black.readthedocs.io/), and [isort](https://pycqa.github.io/isort/) for code style, linting, and import sorting. These tools are enforced both locally and in CI.

### Running Locally

Install all tools:

```sh
uv pip install ruff black isort
```

Check and fix code style:

```sh
ruff check . --fix
black .
isort .
```

Or, to just check (without fixing):

```sh
ruff check .
black --check .
isort --check-only .
```

### Pre-commit Hooks

To automatically run these tools before every commit, install pre-commit and set up the hooks:

```sh
uv pip install pre-commit
pre-commit install
pre-commit run --all-files
```

The configuration is in `.pre-commit-config.yaml`.

### Continuous Integration (CI)

All code style checks (Ruff, Black, isort) are run automatically in GitHub Actions CI on every push and pull request. See `.github/workflows/ci.yml` for details.

### Configuration

All tool configurations are in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
target-version = "py312"
exclude = [
    ".venv",
    "concord232.egg-info",
    "__pycache__",
]

[tool.black]
line-length = 88
target-version = ["py312"]

[tool.isort]
profile = "black"
line_length = 88
skip = [".venv", "concord232.egg-info", "__pycache__"]
```

# Badges

[![CI](https://github.com/r26d/concord232/actions/workflows/ci.yml/badge.svg)](https://github.com/r26d/concord232/actions/workflows/ci.yml)
[![Coverage Status](https://img.shields.io/badge/coverage-27%25-yellow.svg)](coverage.xml)

# Features

- Control and monitor GE Concord 4 alarm panels via RS232
- Home Assistant integration
- HTTP API for remote control
- Command-line client and server
- Extensible and developer-friendly

# Quick Start

1. Install the package:

   ```sh
   pip install concord232
   ```

2. Connect your RS232 adapter and start the server:

   ```sh
   concord232_server --serial /dev/ttyUSB0
   ```

3. Use the client to check status:

   ```sh
   concord232_client summary
   ```

# Project Structure

- `concord232/` - Core library code
- `concord232_client` - Command-line client
- `concord232_server` - Server exposing HTTP API
- `addon-concord232/` - Home Assistant app (formerly add-on; runs the server on HA OS, e.g. Yellow)
- `docs-site/docs/` - Documentation (including [migration guide](docs-site/docs/migration-mac-mini-to-ha-yellow.md) to HA Yellow)
- `tests/` - Test suite
- `README.md` - Project documentation
- `pyproject.toml`, `setup.py` - Packaging and configuration

# Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines (or create one if it does not exist). Typical steps:

- Fork the repository
- Create a new branch
- Make your changes
- Run tests and linting
- Submit a pull request

# License

This project is licensed under the terms of the LICENSE file in this repository.

# Contact & Support

For questions, issues, or feature requests, please open an issue on GitHub or contact the maintainer at <brett@r26d.com>.

---

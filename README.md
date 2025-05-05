GE Concord 4 RS232 Automation Module Interface Library and Server
==================================================================

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

The server must be run on a machine with connectivity to the panel, to get started, you must only supply the serial port.  In this case I use a USB to Serial adapter

```
concord232_server --serial /dev/ttyUSB0 
```

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
options: silent arming, or instant arming.  Silent arming will not
beep while the alarm is setting.  Instant arming has no delay.
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

Home Assistant will automatically download and install the pip3 library, but it only utilizes the Client to connect to the server.  I used the instructions [found here](http://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd/) for setting up the server to run automatically at boot time.

## HTTP API

The concord232 server also exposes a simple HTTP API for interacting with your panel.  
Below are the available endpoints and their usage:

| Endpoint         | Method | Description/Commands                                                                                 |
|------------------|--------|------------------------------------------------------------------------------------------------------|
| `/panel`         | GET    | Get panel state                                                                                      |
| `/zones`         | GET    | Get all zones                                                                                        |
| `/partitions`    | GET    | Get all partitions                                                                                   |
| `/command`       | GET    | `cmd=arm`, `cmd=disarm`, `cmd=keys` (see below for parameters)                                      |
| `/version`       | GET    | Get API version                                                                                      |
| `/equipment`     | GET    | Request all equipment data                                                                           |
| `/all_data`      | GET    | Request dynamic data refresh                                                                         |

### `/command` endpoint

- **Arm the system:**
  - `/command?cmd=arm&level=stay&option=<option>`
  - `/command?cmd=arm&level=away&option=<option>`

- **Disarm the system:**
  - `/command?cmd=disarm&master_pin=<PIN>`

- **Send keys (e.g., *, #, digits):**
  - `/command?cmd=keys&keys=<keys>&group=<group>`
  - Example: To send a `*` key to partition 3:  
    `/command?cmd=keys&keys=*&group=3`

### Example usage

To send a * key to partition 3 using curl:

```sh
curl "http://<your_server_address>:<port>/command?cmd=keys&keys=*&group=3"
```

Replace `<your_server_address>` and `<port>` with your server's address and port.

## Testing

This project uses [pytest](https://pytest.org/) for testing and [uv](https://github.com/astral-sh/uv) as the Python package manager.

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

## Automated Linting

This project uses [Ruff](https://docs.astral.sh/ruff/) for automated linting and code style enforcement. Ruff runs automatically on every push and pull request via GitHub Actions. You can also run it locally:

```sh
uv pip install ruff
ruff check .
```

See `.github/workflows/ci.yml` for the CI configuration.

## Linting

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and code style enforcement.

To check code style and lint your code, run:

```sh
uv pip install ruff
ruff .
```

You can also automatically fix some issues with:

```sh
ruff check . --fix
```

The linter is configured in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
target-version = "py312"
exclude = [
    ".venv",
    "concord232.egg-info",
    "__pycache__",
]
```

> **Note:** Linting is not currently run automatically in CI, so please run it locally before submitting changes.

# Badges

[![CI](https://github.com/yourusername/concord232/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/concord232/actions/workflows/ci.yml)
<!-- Example badges, replace with actual URLs as needed -->
[![Coverage Status](https://img.shields.io/coveralls/github/yourusername/concord232/main.svg)](https://coveralls.io/github/yourusername/concord232?branch=main)

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

For questions, issues, or feature requests, please open an issue on GitHub or contact the maintainer at <your-email@example.com>.

---

## 0.16.5

- Docs: ser2net 8O1 wiring guide (`docs-site/docs/ser2net-8o1-wiring.md`); RFC2217 testing doc links and ser2net example line with parity.

## 0.16.4

- Docs: Advantech EKI-1511L-A — when to use `socket://` vs `rfc2217://`, Telnet IAC troubleshooting, Superbus testing guide (`docs-site`).
- Add `scripts/test_superbus.py` to send Concord frames and inspect ACK / panel messages (repo root on `sys.path`, no install required).
- Improve `scripts/test_rfc2217.py` (TCP preflight, default `socket://`, Concord line settings).
- Serial: optional debug logging for TX/RX and message-loop diagnostics.

## 0.16.3

- Fix broken %-format strings in command type assertion messages
- Fix CI: update test assertion for partition keyword argument
- Bump GitHub Actions to Node.js 24-compatible versions
- Format scripts with black

## 0.16.2

- Fix: serial reconnect crash loop — add post-connect settling delay, drain stale TX queue, and exponential backoff on consecutive reconnects.
- Update configuration files for improved server settings.

## 0.16.1

- Fix: add proper icon.png (256x256) and logo.png so the add-on displays an icon on the HA Apps screen.

## 0.16.0

- Add partition support to arm/disarm commands and fix partition data bug.

## 0.15.10

- Fix: add `[tool.setuptools.packages.find]` to pyproject.toml so all sub-packages (`concord232.server`, `concord232.client`) are installed.

## 0.15.9

- Fix: add `__init__.py` to `concord232/server/` and `concord232/client/` so sub-packages are installed correctly (`No module named 'concord232.server'` resolved).
- Fix: `setup.py` now uses `find_packages()` to include all sub-packages.

## 0.15.8

- Fix: run.sh now invokes `python3 -c "from concord232.main import main; main()"` directly, bypassing the broken pip-generated entry point script entirely.

## 0.15.7

- Fix: Flask API now stays up even if the serial connection fails (non-daemon thread, serial errors caught and logged).

## 0.15.6

- Fix: start Flask API before opening serial port so port 5007 is always reachable even if the serial connection is slow or fails.

## 0.15.5

- Fix: correct `concord232_server` entry point so the server starts correctly inside the add-on container.

## 0.15.4

- Improved documentation (configuration table, Advantech EKI-1511L-A default port). Default serial example set to `rfc2217://`.

## 0.15.3

- Expose port 5007 on the host so the Concord Alarm integration can reach the API.

## 0.15.2 and earlier

- See repository CHANGELOG for full history.

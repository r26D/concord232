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

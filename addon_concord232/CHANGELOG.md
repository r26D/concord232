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

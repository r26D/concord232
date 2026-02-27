# Concord232 Add-on

Runs the concord232 server on your Home Assistant host (e.g. Yellow) so the [Concord Alarm](https://www.home-assistant.io/integrations/concord/) integration can talk to your GE Concord 4 panel over RS232.

## Configuration

| Option  | Required | Description |
|---------|----------|-------------|
| **serial** | Yes | Serial device or URL. Use `/dev/ttyUSB0` (or similar) for a USB–serial adapter plugged into the host, or `rfc2217://host:port` for a network serial server (e.g. ser2net). |
| **port**   | No  | HTTP API port (default: 5007). |
| **log**    | No  | Path to log file inside the container. Leave empty to log to stdout only. |

## Serial connection

- **USB on the Yellow:** Use a USB–RS232 adapter and set `serial` to the device path (e.g. `/dev/ttyUSB0`). The exact name may vary; check the Supervisor → System → Hardware tab or run `ls /dev/tty*` via the SSH add-on.
- **Network serial (RFC2217):** If the panel is connected to another device (e.g. Raspberry Pi) running ser2net or similar, set `serial` to `rfc2217://<host>:<port>`.

## Home Assistant integration

After the add-on is running, add the **Concord Alarm** integration in Home Assistant and set the host to the Yellow’s IP (or `localhost` / `127.0.0.1` if the integration runs on the same host) and port to the value of the add-on **port** option (default 5007).

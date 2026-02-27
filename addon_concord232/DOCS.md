# Concord232

Runs the concord232 server on your Home Assistant host (e.g. Yellow) so the [Concord Alarm](https://www.home-assistant.io/integrations/concord/) integration can talk to your GE Concord 4 panel over RS232.

## Configuration

| Option     | Required | Description |
|------------|----------|-------------|
| **serial** | Yes | Serial device or URL — see _Serial connection_ below. |
| **port**   | No  | HTTP API listen port (default: `5007`). |
| **log**    | No  | Path to a log file inside the container. Leave empty to log to the add-on log only. |

## Serial connection

Set the **serial** option to the path or URL that matches how the RS232 adapter is connected.

### Dedicated network serial server on the LAN (e.g. Advantech EKI-1511L, MOXA NPort, Digi)

Hardware serial servers expose a plain TCP socket in **TCP Server** mode. This is the correct mode — **not** VCOM/Virtual COM, which requires a proprietary Windows driver.

```
socket://192.168.1.100:4660
```

Replace `192.168.1.100` with the device's IP address.

**Port:** check the device's web UI under the serial port → TCP Server settings. Common defaults:
- **Advantech EKI-1511L-A**: `4660`
- **MOXA NPort**: `4001`
- **Digi**: `2101`

### ser2net in RFC2217 mode (Raspberry Pi, another Linux host)

If you have ser2net running on another machine in `telnet` mode (which enables RFC2217 Telnet option negotiation):

```
rfc2217://192.168.1.100:5500
```

> **Important:** ser2net must be configured with `telnet` mode (not `raw`) for RFC2217 to work.
> Example ser2net entry: `5500:telnet:0:/dev/ttyUSB0:9600`

### USB adapter plugged directly into the Yellow

Find the device path using the Terminal & SSH app (`ls /dev/tty*` before and after plugging in):

```
/dev/ttyUSB0
```

## Home Assistant integration

After the app is running, configure the **Concord Alarm** integration in Home Assistant:

- **Host:** `localhost` (if the integration is on the same HA instance as this add-on)
- **Port:** the value of the **port** option (default `5007`)

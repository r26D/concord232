# Concord232

Runs the concord232 server on your Home Assistant host (e.g. Yellow) so the [Concord Alarm](https://www.home-assistant.io/integrations/concord/) integration can talk to your GE Concord 4 panel over RS232.

## Configuration

| Option     | Required | Description                                                                         |
| ---------- | -------- | ----------------------------------------------------------------------------------- |
| **serial** | Yes      | Serial device or URL — see _Serial connection_ below.                               |
| **port**   | No       | HTTP API listen port (default: `5007`).                                             |
| **log**    | No       | Path to a log file inside the container. Leave empty to log to the add-on log only. |

## Serial connection

Set the **serial** option to the path or URL that matches how the RS232 adapter is connected.

### Dedicated network serial server on the LAN (e.g. Advantech EKI-1511L, MOXA NPort, Digi)

Hardware serial servers expose a plain TCP socket in **TCP Server** mode. This is the correct mode — **not** VCOM/Virtual COM, which requires a proprietary Windows driver.

```
socket://192.168.1.100:4660
```

Replace `192.168.1.100` with the device's IP address.

**Port:** check the device's web UI under the serial port → TCP Server settings. Common defaults:

- **Advantech EKI-1511L-A**: `5500`
- **MOXA NPort**: `4001`
- **Digi**: `2101`

#### Advantech EKI-1511L-A (RS-232 to Ethernet)

Use this device in **TCP Server** mode so it listens for incoming TCP connections and forwards bytes to the Concord **automation module** RS-232 port.

1. Give the EKI a fixed IP on your LAN (web UI).
2. Set **Operation mode** to **TCP Server** (raw TCP to the serial port — not VCOM).
3. If the UI offers **Telnet** vs **raw / transparent / RFC 2217** for the TCP connection, choose **raw or transparent** so bytes pass through unchanged. **Telnet mode** injects negotiation bytes (`0xff` IAC) and will break Concord; `scripts/test_superbus.py` will show `ff fb …` in RX instead of **`06`** (ACK).
4. On the **serial** settings page, match the panel: **9600 baud**, **8 data bits**, **odd parity**, **1 stop bit**, no flow control (same line format `concord232` uses).
5. In this add-on, set **serial** to `socket://<EKI_IP>:<port>` (default port is often **5500** — confirm in the UI).

Use **`socket://`**, not `rfc2217://`. The EKI exposes plain TCP; it does not perform RFC2217 Telnet parameter negotiation.

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

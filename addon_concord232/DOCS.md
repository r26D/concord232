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
3. On the **serial** settings page, match the panel: **9600 baud**, **8 data bits**, **odd parity**, **1 stop bit**, no flow control (same line format `concord232` uses).
4. **TCP URL in this add-on** — pick one:
   - **`socket://<EKI_IP>:<port>`** — Use when the EKI forwards **only** RS-232 octets on TCP (true raw / transparent). Best if `scripts/test_superbus.py` shows **`06`** (ACK) or **`0a`** (message start), not `ff fb …`.
   - **`rfc2217://<EKI_IP>:<port>`** — Use when the device speaks **Telnet** on TCP: a plain `socket://` connection may show only **`ff`** (IAC) negotiation in RX. PySerial’s RFC2217 client completes Telnet setup and exposes a clean serial stream; some EKI firmware needs this. If open fails with “Remote does not accept parameter change”, try the other URL or adjust the EKI’s RFC2217/Telnet options per its manual.

Default port is often **5500** — confirm in the UI.

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

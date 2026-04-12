# Testing network serial (RFC2217 or raw TCP)

Use `scripts/test_rfc2217.py` to verify that a **socket** or **RFC2217** URL is reachable and that pyserial can open it. The default URL is **`socket://192.168.3.89:5500`**, matching the Home Assistant add-on default — many bridges use raw TCP and do **not** complete RFC2217 parameter negotiation.

**Hardware serial servers** (e.g. **Advantech EKI-1511L-A** in TCP Server mode) forward RS-232 over plain TCP. Use **`socket://ip:port`** (often port **5500** on the EKI). Set **9600 8O1** on the device’s serial settings to match the Concord automation module; see the add-on `DOCS.md` for a full EKI checklist.

If TCP works but you still see **timeouts** and **`reader thread died`**, fix **8O1 parity**, **ser2net telnet/RFC2217 mode**, and **wiring** first—see [ser2net, 8O1 serial, and wiring](ser2net-8o1-wiring.md).

## Quick checks (no Python)

1. **Port open**  
   From a machine on the same network:
   ```bash
   nc -zv 192.168.3.89 5500
   ```
   or:
   ```bash
   telnet 192.168.3.89 5500
   ```
   If the port is open, you get a connection (telnet may show Telnet option negotiation; Ctrl+] then `quit` to exit).

2. **ser2net must be in telnet mode**  
   For RFC2217 to work, the server (e.g. ser2net) must use **telnet** mode, not **raw**. The serial device should be **9600 8O1** (odd parity). Example ser2net 3.x–style line (keywords may vary by version; see [ser2net, 8O1 serial, and wiring](ser2net-8o1-wiring.md)):
   ```text
   5500:telnet:0:/dev/ttyUSB0:9600 ODD 8DATABITS 1STOPBIT
   ```

## Python script (same as concord232)

From the project root, with the concord232 environment installed (e.g. `pip install -e .` or `pip install pyserial`):

```bash
python scripts/test_rfc2217.py
```

To test RFC2217 explicitly (only if your server negotiates baud/parity over Telnet):

```bash
python scripts/test_rfc2217.py rfc2217://192.168.3.89:5500
```

### `Remote does not accept parameter change (RFC2217)`

TCP connects, but pyserial fails during RFC2217 subnegotiation (baudrate, parity, etc.). Your serial bridge is probably **raw TCP** or does not implement full RFC2217.

**Fix:** Use **`socket://host:port`** in the add-on / `config.ini` `[server] serial` — same host and port. The line speed and parity are applied on the device running ser2net/socat (e.g. 9600 8O1 for the Concord automation module), not over RFC2217.

- **Success:** “Connected successfully” and exit code 0.
- **Failure:** Error message (e.g. connection refused, timeout) and exit code 1.

**`Could not open port … timed out`** (from pyserial) means the **TCP connection** to `host:port` did not complete. That is a network reachability problem (wrong IP/subnet, device offline, ser2net not listening, or firewall), not the Concord serial protocol. The script runs a **TCP preflight** first so you see whether plain `socket.connect` works.

The script opens the URL with pyserial (same as the concord232 server), does a short read, then closes. No data is required from the panel for the connection test to succeed.

## Troubleshooting dropped connections

**Symptoms**

- Log lines like `Unable to send message (timeout), too many attempts` — the server is not receiving an ACK from the panel within the retry window. Often appears together with network or serial-server issues.
- `serial.serialutil.SerialException: connection failed (reader thread died)` — the RFC2217 TCP session to ser2net (or similar) closed; pyserial’s background reader exited.

**Typical causes**

- ser2net or the serial device restarted; Wi‑Fi or Ethernet blip; wrong ser2net mode (must be **telnet**, not raw, for `rfc2217://`).
- Physical USB/RS-232 path to the panel unplugged or the automation module not powered.

**Recovery**

Recent server builds reconnect automatically: the serial loop closes the dead port, waits a few seconds, opens the same URL again, and re-requests zone and dynamic data. Until the link is healthy again, the HTTP API may stay up while panel commands fail or time out.

**Checks**

- Confirm `nc -zv host 5500` (or your port) from the host running concord232.
- On the ser2net box, confirm the device node still exists and ser2net logs show a stable session.

## Next: panel protocol

Once TCP/`socket://` works, test **ACK** and panel messages with the Superbus automation module: [Testing the Superbus Automation Module](testing-superbus.md).

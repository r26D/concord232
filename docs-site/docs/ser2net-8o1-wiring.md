# ser2net, 8O1 serial, and wiring

Concord232 opens the serial port as **9600 baud, 8 data bits, odd parity, 1 stop bit (8O1)**. That must match the **physical link** to the GE Concord automation module and whatever exposes `/dev/ttyUSB0` (or similar) on the machine running **ser2net**. If the port is configured as **8N1** (no parity) or the wrong baud, the panel will usually **not ACK** messages—you will see `Unable to send message (timeout)` and hex payloads like `022022` / `03020308` in the logs even when TCP to ser2net works.

This page is the checklist to fix **line settings**, **ser2net RFC2217/telnet mode**, and **wiring** before changing Python code.

## 1. Line settings (must match the panel)

| Parameter | Value used by Concord232 |
|-----------|---------------------------|
| Baud | 9600 |
| Data bits | 8 |
| Parity | **Odd** |
| Stop bits | 1 |

On the Linux host attached to the USB–serial adapter, confirm the device is opened with **8O1**, not 8N1. Concord232 sets this when using `rfc2217://` (RFC2217 negotiates line settings with the server), but **ser2net must actually apply 8O1 to the real serial device**.

## 2. ser2net: telnet mode (required for `rfc2217://`)

PySerial’s `rfc2217://host:port` URL expects a **Telnet**-style RFC2217 server, **not** a raw TCP-to-serial pipe.

- **Wrong:** Raw TCP forwarding where bytes pass through with no Telnet/RFC2217 negotiation (often labeled “raw” in configs).
- **Right:** A ser2net **telnet** listener so the client can set baud/parity and the server maps that to the serial port.

### ser2net 3.x (`/etc/ser2net.conf` style)

Conceptual form (adjust device path, port, and **device options** per `man ser2net` on your system):

```text
5500:telnet:0:/dev/ttyUSB0:9600 ODD 8DATABITS 1STOPBIT
```

The third field is the telnet banner timeout; `0` is common. The last segment is **device name** and **serial parameters**. Option order and keywords vary by ser2net version (e.g. `ODD` vs `ODDPARITY`)—use **`man ser2net`** on your system and validate with `stty` or a loopback test if unsure.

After editing, restart ser2net and verify it listens on the chosen TCP port.

### ser2net 4.x (YAML)

Use the layout described in your distribution’s docs; set the **serial connector** to **9600 8O1** (or the equivalent option names in v4). Ensure the **acceptor** is the Telnet/RFC2217-capable profile, not raw-only.

### Verify from the ser2net host

With the port idle, you can use `stty` on the device (if nothing else holds it open) to confirm parity, or watch **ser2net logs** when Concord232 connects—misconfigured parity often shows no panel traffic or immediate timeouts.

## 3. Wiring and hardware

Concord232 cannot fix:

- **TX/RX** reversed (need a null-modem or correct cable for your chain).
- **Missing common ground** between adapter and automation module.
- **Automation module** not powered or not seated correctly on the panel bus.
- **Wrong serial standard** (e.g. RS-232 vs TTL) for your adapter—use an adapter that matches the automation module’s electrical spec per GE/Interlogix documentation.

Work through the panel and module install guides: many issues present as **no ACKs** and **reader thread died** if the link flaps when the panel or ser2net resets.

## 4. Order of operations

1. Confirm **TCP**: `nc -zv <ser2net-host> <port>` from the Home Assistant host (or wherever Concord232 runs).
2. Confirm **ser2net** uses **telnet/RFC2217**, not raw, and the **serial side is 9600 8O1**.
3. Confirm **physical** RS-232 path and automation module per manufacturer docs.
4. If timeouts persist, capture **ser2net** logs during a failure to see disconnect reasons.

## See also

- [Testing RFC2217 serial connection](testing-rfc2217.md) — quick connectivity test and symptom list.
- [Migration / HA Yellow](migration-mac-mini-to-ha-yellow.md) — deployment notes if applicable.

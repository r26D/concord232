# Testing the Superbus Automation Module

After [network serial](testing-rfc2217.md) reaches your bridge (e.g. Advantech EKI-1511L-A), use **`scripts/test_superbus.py`** to send real Concord automation frames and inspect **ACK**, **NAK**, and panel messages (lines starting with **LF `0x0A`**).

## Requirements

- Serial path configured for **9600 baud, 8 data bits, odd parity, 1 stop** on the **EKI** (or your RS-232 adapter), matching `concord232`.
- Concord **Superbus Automation Module** powered and wired to that RS-232 port.

## Usage

From the repository root (no install required — the script adds the repo to `sys.path`):

```bash
python scripts/test_superbus.py socket://192.168.3.89:5500
```

You can also use `pip install -e .` and run the same command from anywhere, if you prefer.

Default URL if omitted: `socket://192.168.3.89:5500`.

### Options

| Flag | Meaning |
|------|--------|
| `--request dynamic` | Send **Dynamic Data Refresh** (default; lightest request). |
| `--request full` | Full equipment list request. |
| `--request zones` / `partitions` | Single equipment list for zones or partitions. |
| `--request all` | Sends `full`, `zones`, `partitions`, `dynamic` in order. |
| `--after-send 3` | Seconds to collect RX after each transmit (default `3`). |
| `--settle 1` | Seconds to wait after opening the port before first TX. |
| `--flush-rx` | Clear the RX buffer before each transmit (cleaner trace). |
| `--listen-only 5` | Do not send anything; only read for 5 seconds (spontaneous panel traffic). |

### What “good” looks like

- **`ACK`** (`0x06`) after a request usually means the automation module accepted the frame.
- **`MSG_START(LF)`** (`0x0A`) begins a panel → host message (ASCII hex payload follows, as in the main server).
- **`NAK`** (`0x15`) means the module rejected the frame (checksum/format).

If you see **no ACK and no LF** in the window, verify wiring, EKI parity, and that the automation module is enrolled and active on the panel.

### RX shows only `ff fb …` / `ff fd …` (Telnet IAC)

If the hex dump looks like `ff fb 03 ff fb 01 ff fe 01 ff fd 00` and never **`06`** (ACK) or **`0a`** (message start), the TCP session is carrying **Telnet option negotiation** (`0xff` = IAC), not raw RS-232 bytes from the Superbus module.

**Fix (EKI / device server):**

1. **Prefer raw TCP on the device** — In the web UI, set the TCP/serial mode to **raw / transparent / binary** so the TCP stream is only RS-232 bytes.

2. **Or use `rfc2217://` in concord232** — If the EKI always uses Telnet on that port and you still see `ff fb …` with `socket://`, try **`rfc2217://host:port`** instead. PySerial negotiates Telnet/RFC2217 and presents a normal serial byte stream; many users see **`0a`** (panel messages) with this URL even when `socket://` only showed IAC bytes.

Re-run `scripts/test_superbus.py` with the same URL you will use in the server.

## See also

- Add-on serial notes: `addon_concord232/DOCS.md`
- Full server: `concord232_server --serial socket://... --debug`

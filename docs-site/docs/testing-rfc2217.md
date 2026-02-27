# Testing RFC2217 serial connection

Use this to verify that `rfc2217://192.168.3.89:5500` (or any RFC2217 URL) is reachable and that pyserial can open it.

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
   For RFC2217 to work, the server (e.g. ser2net) must use **telnet** mode, not **raw**. Example ser2net line:
   ```text
   5500:telnet:0:/dev/ttyUSB0:9600
   ```

## Python script (same as concord232)

From the project root, with the concord232 environment installed (e.g. `pip install -e .` or `pip install pyserial`):

```bash
python scripts/test_rfc2217.py
```

To test a different URL:

```bash
python scripts/test_rfc2217.py rfc2217://192.168.3.89:5500
```

- **Success:** “Connected successfully” and exit code 0.
- **Failure:** Error message (e.g. connection refused, timeout) and exit code 1.

The script opens the URL with pyserial (same as the concord232 server), does a short read, then closes. No data is required from the panel for the connection test to succeed.

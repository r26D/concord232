#!/usr/bin/env python3
"""
Test connectivity to a network serial port (RFC2217 or raw socket).
Usage: python test_rfc2217.py [URL]
  URL examples:
    rfc2217://192.168.3.89:5500   (ser2net telnet mode; server must accept params)
    socket://192.168.3.89:5500   (raw TCP; use if RFC2217 param change is rejected)
Default: rfc2217://192.168.3.89:5500
"""
import sys

try:
    import serial
except ImportError:
    print("Install pyserial first: pip install pyserial")
    sys.exit(1)


def test_serial_url(
    url: str = "rfc2217://192.168.3.89:5500", timeout: float = 2.0
) -> bool:
    """Open the serial URL and perform a brief read. Returns True if connection works."""
    print(f"Connecting to {url} (timeout={timeout}s)...")
    try:
        ser = serial.serial_for_url(
            url,
            baudrate=9600,
            timeout=timeout,
        )
        print("  Connected successfully.")
        # Optional: try one non-blocking read to see if the link is alive
        ser.timeout = 0.1
        data = ser.read(1)
        if data:
            print(f"  Read 1 byte: {data!r}")
        else:
            print("  No data available (OK if panel is idle).")
        ser.close()
        return True
    except serial.SerialException as e:
        msg = str(e)
        print(f"  Error: {msg}")
        if "Remote does not accept parameter change (RFC2217)" in msg:
            print()
            print("  Hint: Your server may not support RFC2217 parameter negotiation.")
            print("  Try raw TCP instead, e.g.:")
            if url.startswith("rfc2217://"):
                hostport = url.replace("rfc2217://", "", 1)
                print(f"    python scripts/test_rfc2217.py socket://{hostport}")
            print(
                "  In addon config, set serial to socket://host:port (same host:port)."
            )
        return False
    except OSError as e:
        print(f"  OS/network error: {e}")
        return False


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "rfc2217://192.168.3.89:5500"
    ok = test_serial_url(url)
    sys.exit(0 if ok else 1)

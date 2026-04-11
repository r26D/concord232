#!/usr/bin/env python3
"""
Test connectivity to a network serial port (RFC2217 or raw socket).
Usage: python test_rfc2217.py [URL]
  URL examples:
    socket://192.168.3.89:5500   (raw TCP; default — matches typical ser2net raw: or socat)
    rfc2217://192.168.3.89:5500  (full RFC2217; ser2net must accept baud/parity negotiation)
Default: socket://192.168.3.89:5500 (same as addon_concord232 default)
"""

from __future__ import annotations

import socket
import sys
from typing import Optional, Tuple
from urllib.parse import urlparse

try:
    import serial
except ImportError:
    print("Install pyserial first: pip install pyserial")
    sys.exit(1)


def _host_port_from_url(url: str) -> Optional[Tuple[str, int]]:
    """Return (host, port) for rfc2217:// or socket:// URLs, else None."""
    p = urlparse(url)
    if p.scheme not in ("rfc2217", "socket"):
        return None
    if not p.hostname or p.port is None:
        return None
    return p.hostname, p.port


def _tcp_preflight(host: str, port: int, timeout: float) -> bool:
    """Try a plain TCP connect; same failure mode as pyserial's first step."""
    print(f"TCP preflight: {host}:{port} (connect timeout={timeout}s)...")
    try:
        with socket.create_connection((host, port), timeout=timeout):
            print("  TCP connect OK.")
        return True
    except OSError as e:
        print(f"  TCP connect failed: {e}")
        print()
        print("  This means nothing is accepting connections at that address yet.")
        print("  Fix the network path before pyserial can help:")
        print(
            "    - Is the serial bridge / ser2net host online? Same subnet as this machine?"
        )
        print("    - Is ser2net (or similar) listening on that port?")
        print("    - Firewall on {} allowing inbound TCP port {} ?".format(host, port))
        print()
        print("  Quick checks from this machine:")
        print(f"    ping -c 2 {host}")
        print(f"    nc -zv {host} {port}")
        return False


def test_serial_url(
    url: str = "socket://192.168.3.89:5500", timeout: float = 2.0
) -> bool:
    """Open the serial URL and perform a brief read. Returns True if connection works."""
    hp = _host_port_from_url(url)
    if hp:
        host, port = hp
        if not _tcp_preflight(host, port, min(timeout, 10.0)):
            return False
        print()

    print(f"Opening pyserial URL {url} (read timeout={timeout}s)...")
    try:
        ser = serial.serial_for_url(
            url,
            baudrate=9600,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=timeout,
        )
        print("  Connected successfully.")
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
        if "timed out" in msg.lower() and "Could not open port" in msg:
            print()
            print("  (If TCP preflight passed but this still timed out, the failure is")
            print(
                "   likely during RFC2217/Telnet negotiation — use telnet mode on ser2net.)"
            )
        if "Remote does not accept parameter change (RFC2217)" in msg:
            print()
            print("  The TCP link works, but the remote side did not complete RFC2217")
            print(
                "  baud/parity negotiation. Common with ser2net **raw** mode or bridges"
            )
            print("  that only forward bytes (no RFC2217).")
            print()
            print(
                "  Use raw TCP in concord232 (serial line speed is set on the bridge):"
            )
            if url.startswith("rfc2217://"):
                hostport = url.replace("rfc2217://", "", 1).split("?")[0]
                print(f"    python scripts/test_rfc2217.py socket://{hostport}")
            print("  Home Assistant add-on: set `serial` to `socket://host:port`.")
            print("  Optional: configure ser2net with `telnet` and full RFC2217 if you")
            print(
                "  need `rfc2217://` (not required for Concord232 when using socket://)."
            )
        return False
    except OSError as e:
        print(f"  OS/network error: {e}")
        return False


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "socket://192.168.3.89:5500"
    ok = test_serial_url(url)
    sys.exit(0 if ok else 1)

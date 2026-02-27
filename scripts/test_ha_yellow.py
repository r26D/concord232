#!/usr/bin/env python3
"""
Test that Home Assistant Yellow (or HA host) is responding at a given IP.
Checks: host reachable (TCP), optional HTTP on port 8123 (HA) and 5007 (Concord232).
Usage: python test_ha_yellow.py [host] [--port PORT] [--no-8123] [--no-5007]
Default host: 192.168.4.36
"""
import argparse
import socket
import sys


def tcp_reachable(host: str, port: int, timeout: float = 3.0) -> bool:
    """Return True if host:port accepts a TCP connection."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error, OSError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Test HA Yellow reachability")
    parser.add_argument(
        "host",
        nargs="?",
        default="192.168.4.36",
        help="HA Yellow IP (default: 192.168.4.36)",
    )
    parser.add_argument(
        "--port", type=int, help="Only check this port (skip 8123/5007)"
    )
    parser.add_argument(
        "--no-8123", action="store_true", help="Skip HA frontend port 8123"
    )
    parser.add_argument(
        "--no-5007", action="store_true", help="Skip Concord232 API port 5007"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=3.0,
        help="Socket timeout in seconds (default: 3)",
    )
    args = parser.parse_args()

    host = args.host
    timeout = args.timeout
    ok = True

    if args.port is not None:
        if tcp_reachable(host, args.port, timeout):
            print(f"  {host}:{args.port} – reachable")
        else:
            print(f"  {host}:{args.port} – not reachable")
            ok = False
        return 0 if ok else 1

    print(f"Testing HA Yellow at {host} (timeout={timeout}s)...")
    if not args.no_8123:
        if tcp_reachable(host, 8123, timeout):
            print("  8123 (HA frontend) – reachable")
        else:
            print("  8123 (HA frontend) – not reachable")
            ok = False
    if not args.no_5007:
        if tcp_reachable(host, 5007, timeout):
            print("  5007 (Concord232 API) – reachable")
        else:
            print("  5007 (Concord232 API) – not reachable")
            ok = False

    if ok:
        print("  All checked ports responding.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

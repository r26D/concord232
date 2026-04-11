#!/usr/bin/env python3
"""
Exercise the GE Concord Superbus Automation Module over serial (USB, EKI, etc.).

Sends the same framed requests as concord232 (line feed + ASCII hex + checksum),
then records bytes for a short window so you can see ACK/NAK and panel messages.

Usage (from repository root; adds repo to sys.path so no pip install is required):
  python scripts/test_superbus.py
  python scripts/test_superbus.py socket://192.168.3.89:5500 --request all
  python scripts/test_superbus.py --listen-only 5
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Callable, List

# Run with `python scripts/test_superbus.py` from the repo root without `pip install -e .`.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import serial  # noqa: E402

from concord232.concord import (  # noqa: E402
    CONCORD_BAUD,
    CONCORD_BYTESIZE,
    CONCORD_PARITY,
    CONCORD_STOPBITS,
    MSG_START,
    compute_checksum,
    encode_message_to_ascii,
)
from concord232.concord_commands import (  # noqa: E402
    EQPT_LIST_REQ_TYPES,
    build_cmd_equipment_list,
    build_dynamic_data_refresh,
)


def open_serial(url: str, read_timeout: float) -> serial.Serial:
    return serial.serial_for_url(
        url,
        baudrate=CONCORD_BAUD,
        bytesize=CONCORD_BYTESIZE,
        parity=CONCORD_PARITY,
        stopbits=CONCORD_STOPBITS,
        timeout=read_timeout,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False,
    )


def build_tx_payload(body: List[int]) -> List[int]:
    """Append checksum the same way as AlarmPanelInterface.enqueue_msg_for_tx."""
    msg = body[:]
    msg.append(compute_checksum(msg))
    return msg


def frame_for_wire(msg_with_checksum: List[int]) -> bytes:
    framed = MSG_START + encode_message_to_ascii(msg_with_checksum)
    return framed.encode("latin-1")


def describe_control_byte(b: int) -> str:
    if b == 0x06:
        return "ACK"
    if b == 0x15:
        return "NAK"
    if b == 0x0A:
        return "MSG_START(LF)"
    return ""


def format_rx(data: bytes) -> str:
    if not data:
        return "  (no bytes)"
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i : i + 16]
        hx = chunk.hex(" ")
        ann = []
        for j, byte in enumerate(chunk):
            label = describe_control_byte(byte)
            if label:
                ann.append(f"@{i+j}:{label}")
        extra = f"  {' '.join(ann)}" if ann else ""
        lines.append(f"  {hx}{extra}")
    return "\n".join(lines)


def read_for_seconds(ser: serial.Serial, seconds: float, chunk_timeout: float) -> bytes:
    """Collect all bytes until *seconds* wall time elapses."""
    ser.timeout = chunk_timeout
    end = time.monotonic() + seconds
    out = bytearray()
    while time.monotonic() < end:
        chunk = ser.read(4096)
        if chunk:
            out.extend(chunk)
    return bytes(out)


REQUEST_BUILDERS: dict[str, Callable[[], List[int]]] = {
    "dynamic": build_dynamic_data_refresh,
    "full": lambda: build_cmd_equipment_list(0),
    "zones": lambda: build_cmd_equipment_list(EQPT_LIST_REQ_TYPES["ZONE_DATA"]),
    "partitions": lambda: build_cmd_equipment_list(EQPT_LIST_REQ_TYPES["PART_DATA"]),
}


def run() -> int:
    parser = argparse.ArgumentParser(
        description="Send Concord automation requests and print raw responses."
    )
    parser.add_argument(
        "serial_url",
        nargs="?",
        default="socket://192.168.3.89:5500",
        help="pyserial URL (default: %(default)s)",
    )
    parser.add_argument(
        "--settle",
        type=float,
        default=1.0,
        metavar="SEC",
        help="Sleep after open before first TX (default: %(default)s)",
    )
    parser.add_argument(
        "--request",
        choices=list(REQUEST_BUILDERS.keys()) + ["all"],
        default="dynamic",
        help="Which request to send (default: %(default)s)",
    )
    parser.add_argument(
        "--after-send",
        type=float,
        default=3.0,
        metavar="SEC",
        help="How long to read RX after each transmit (default: %(default)s)",
    )
    parser.add_argument(
        "--listen-only",
        type=float,
        default=None,
        metavar="SEC",
        help="Do not transmit; only read for this many seconds",
    )
    parser.add_argument(
        "--flush-rx",
        action="store_true",
        help="Clear input buffer before each transmit (cleaner trace; may drop async panel traffic)",
    )
    args = parser.parse_args()

    print(f"Opening {args.serial_url} (9600 8O1)...")
    try:
        ser = open_serial(args.serial_url, read_timeout=0.05)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        if args.settle > 0:
            print(f"Settling {args.settle:.1f}s...")
            time.sleep(args.settle)

        if args.listen_only is not None:
            print(f"Listen-only for {args.listen_only:.1f}s (no TX)...")
            data = read_for_seconds(ser, args.listen_only, 0.05)
            print(format_rx(data))
            return 0

        order: List[str]
        if args.request == "all":
            order = ["full", "zones", "partitions", "dynamic"]
        else:
            order = [args.request]

        for name in order:
            body = REQUEST_BUILDERS[name]()
            msg = build_tx_payload(body)
            wire = frame_for_wire(msg)

            print()
            print(f"--- Request: {name} ---")
            print(f"  Payload (+checksum): {' '.join(f'{b:02x}' for b in msg)}")
            print(f"  On wire ({len(wire)} bytes): {wire.hex(' ')}")

            if args.flush_rx:
                ser.reset_input_buffer()

            ser.write(wire)
            ser.flush()

            data = read_for_seconds(ser, args.after_send, 0.05)
            print(f"  RX ({len(data)} bytes) over {args.after_send:.1f}s:")
            print(format_rx(data))

            ack = b"\x06" in data
            nak = b"\x15" in data
            lf = b"\x0a" in data
            hints = []
            if ack:
                hints.append("saw ACK (0x06)")
            if nak:
                hints.append("saw NAK (0x15)")
            if lf:
                hints.append("saw message start LF (0x0A)")
            if hints:
                print("  Summary: " + "; ".join(hints))
            else:
                print(
                    "  Summary: no ACK/NAK/LF in window — check EKI serial "
                    "(9600 8O1), cable, and panel/automation power."
                )
            if b"\xff" in data and not (ack or nak or lf):
                print(
                    "  Note: 0xFF bytes are often Telnet IAC negotiation. "
                    "Prefer raw TCP / binary mode on the device server so only "
                    "RS-232 bytes are forwarded."
                )

        return 0
    finally:
        ser.close()


if __name__ == "__main__":
    sys.exit(run())

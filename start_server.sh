#!/bin/bash

# start_server.sh - Start the Concord232 server with RFC2217 serial connection
# Usage: ./start_server.sh [--serial SERIAL_URL] [--port PORT] [additional args]
# Example: ./start_server.sh --serial rfc2217://192.168.3.89:5500 --port 5008

# Default values
SERIAL_URL="rfc2217://192.168.3.89:5500"
PORT=5008

# Allow overrides from command line
ARGS=()
while [[ $# -gt 0 ]]; do
  case $1 in
    --serial)
      SERIAL_URL="$2"
      shift 2
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    *)
      ARGS+=("$1")
      shift
      ;;
  esac
done

# Start the server
exec ./concord232_server --serial "$SERIAL_URL" --port "$PORT" "${ARGS[@]}" 
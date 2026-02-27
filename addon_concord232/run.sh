#!/bin/sh
set -e

# Read options from Home Assistant (written to /data/options.json)
SERIAL="$(jq -r '.serial // empty' /data/options.json)"
PORT="$(jq -r '.port // 5007' /data/options.json)"
LOG="$(jq -r '.log // empty' /data/options.json)"

if [ -z "$SERIAL" ]; then
  echo "Error: 'serial' option is required. Set it in the add-on configuration (e.g. /dev/ttyUSB0 or rfc2217://host:port)."
  exit 1
fi

EXTRA=""
[ -n "$LOG" ] && EXTRA="$EXTRA --log $LOG"

exec python3 -c "from concord232.main import main; main()" --serial "$SERIAL" --listen 0.0.0.0 --port "${PORT}" $EXTRA

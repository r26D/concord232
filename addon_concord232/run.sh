#!/bin/sh
set -e

# Read options from Home Assistant (written to /data/options.json)
SERIAL="$(jq -r '.serial // empty' /data/options.json)"
PORT="$(jq -r '.port // 5007' /data/options.json)"
LOG="$(jq -r '.log // empty' /data/options.json)"
MQTT_HOST="$(jq -r '.mqtt_host // empty' /data/options.json)"
MQTT_PORT="$(jq -r '.mqtt_port // 1883' /data/options.json)"
MQTT_USERNAME="$(jq -r '.mqtt_username // empty' /data/options.json)"
MQTT_PASSWORD="$(jq -r '.mqtt_password // empty' /data/options.json)"
MQTT_TOPIC_PREFIX="$(jq -r '.mqtt_topic_prefix // "concord232"' /data/options.json)"
MQTT_PUBLISH_TOUCHPAD="$(jq -r '.mqtt_publish_touchpad // true' /data/options.json)"
MQTT_TLS="$(jq -r '.mqtt_tls // false' /data/options.json)"

if [ -z "$SERIAL" ]; then
  echo "Error: 'serial' option is required. Set it in the add-on configuration (e.g. /dev/ttyUSB0 or rfc2217://host:port)."
  exit 1
fi

set -- python3 -c "from concord232.main import main; main()" \
  --serial "$SERIAL" --listen 0.0.0.0 --port "${PORT}"

[ -n "$LOG" ] && set -- "$@" --log "$LOG"

if [ -n "$MQTT_HOST" ]; then
  set -- "$@" --mqtt-host "$MQTT_HOST" --mqtt-port "${MQTT_PORT}" --mqtt-topic-prefix "$MQTT_TOPIC_PREFIX"
  [ -n "$MQTT_USERNAME" ] && set -- "$@" --mqtt-username "$MQTT_USERNAME"
  [ -n "$MQTT_PASSWORD" ] && set -- "$@" --mqtt-password "$MQTT_PASSWORD"
  if [ "$MQTT_PUBLISH_TOUCHPAD" != "true" ]; then
    set -- "$@" --mqtt-no-touchpad
  fi
  if [ "$MQTT_TLS" = "true" ]; then
    set -- "$@" --mqtt-tls
  fi
fi

exec "$@"

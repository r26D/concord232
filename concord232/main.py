import argparse
import configparser
import logging
import logging.handlers
import os
import ssl
import threading
from typing import Any

from concord232 import concord
from concord232.mqtt_events import PanelMqttPublisher
from concord232.server import api

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None  # type: ignore[assignment]

LOG_FORMAT = "%(asctime)-15s %(module)s %(levelname)s %(message)s"


def _setup_mqtt(
    ctrl: Any,
    *,
    host: str,
    port: int,
    username: str,
    password: str,
    topic_prefix: str,
    client_id: str,
    publish_touchpad: bool,
    tls: bool,
    logger: logging.Logger,
) -> None:
    if mqtt is None:
        logger.error("MQTT requested but paho-mqtt is not installed")
        return
    client = mqtt.Client(client_id=client_id, clean_session=True)
    if username:
        client.username_pw_set(username, password)
    if tls:
        client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)
    try:
        client.connect(host, port, 60)
    except Exception:
        logger.exception("MQTT connect failed; continuing without MQTT")
        return
    client.loop_start()
    publisher = PanelMqttPublisher(
        client,
        topic_prefix,
        publish_touchpad=publish_touchpad,
        logger=logger,
    )
    publisher.publish_online()
    ctrl.register_message_handler("ALARM", publisher.publish_alarm)
    if publish_touchpad:
        ctrl.register_message_handler("TOUCHPAD", publisher.publish_touchpad)
    logger.info(
        "MQTT panel events enabled prefix=%s host=%s:%s",
        topic_prefix,
        host,
        port,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GE Concord 4 RS232 Serial Interface Server. Provides a Flask API for interacting with the alarm panel.",
        epilog="""
Example usage:
  concord232_server --serial /dev/ttyUSB0 --config myconfig.ini --debug

For more information, see: https://github.com/JasonCarter80/concord232
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        default="config.ini",
        metavar="FILE",
        help="Path to config file (default: config.ini)",
    )
    parser.add_argument(
        "--debug",
        default=False,
        action="store_true",
        help="Enable debug logging output",
    )
    parser.add_argument(
        "--log",
        default=None,
        metavar="FILE",
        help="Path to log file (default: none; logs to stdout if not set)",
    )
    parser.add_argument(
        "--serial",
        default=None,
        metavar="PORT",
        help="Serial port to open for stream (e.g., /dev/ttyUSB0 or COM3) [REQUIRED]",
    )
    parser.add_argument(
        "--listen",
        default=None,
        metavar="ADDR",
        help="Listen address for the API server (default: 0.0.0.0, all interfaces)",
    )
    parser.add_argument(
        "--port",
        default=None,
        type=int,
        help="Listen port for the API server (default: 5007)",
    )
    parser.add_argument(
        "--mqtt-host",
        default=None,
        metavar="HOST",
        help="MQTT broker host; enables MQTT panel events when set (or use [mqtt] host in config)",
    )
    parser.add_argument(
        "--mqtt-port",
        default=None,
        type=int,
        metavar="PORT",
        help="MQTT broker port (default: 1883 or [mqtt] port)",
    )
    parser.add_argument(
        "--mqtt-username",
        default=None,
        metavar="USER",
        help="MQTT username (optional)",
    )
    parser.add_argument(
        "--mqtt-password",
        default=None,
        metavar="PASS",
        help="MQTT password (optional)",
    )
    parser.add_argument(
        "--mqtt-topic-prefix",
        default=None,
        metavar="PREFIX",
        help="MQTT topic prefix for events (default: concord232)",
    )
    parser.add_argument(
        "--mqtt-client-id",
        default=None,
        metavar="ID",
        help="MQTT client id (default: concord232)",
    )
    parser.add_argument(
        "--mqtt-no-touchpad",
        default=False,
        action="store_true",
        help="Do not publish TOUCHPAD messages to MQTT",
    )
    parser.add_argument(
        "--mqtt-tls",
        default=False,
        action="store_true",
        help="Use TLS for MQTT (also see [mqtt] tls in config)",
    )
    args = parser.parse_args()

    # Load config file
    config = configparser.ConfigParser()
    config.read(args.config)
    cfg = config["server"] if "server" in config else {}
    mqtt_cfg = config["mqtt"] if "mqtt" in config else {}

    # Use config values if CLI args are not set
    serial = args.serial or cfg.get("serial")
    listen = args.listen or cfg.get("listen", "0.0.0.0")
    port = args.port or int(cfg.get("port", 5007))
    log_file = args.log or cfg.get("log")

    mqtt_host = (args.mqtt_host or mqtt_cfg.get("host") or "").strip()
    mqtt_port = args.mqtt_port
    if mqtt_port is None:
        mqtt_port = int(mqtt_cfg.get("port", 1883))
    mqtt_username = args.mqtt_username
    if mqtt_username is None:
        mqtt_username = mqtt_cfg.get("username") or ""
    mqtt_password = args.mqtt_password
    if mqtt_password is None:
        mqtt_password = mqtt_cfg.get("password") or ""
    mqtt_topic_prefix = args.mqtt_topic_prefix or mqtt_cfg.get(
        "topic_prefix", "concord232"
    )
    mqtt_client_id = args.mqtt_client_id or mqtt_cfg.get("client_id", "concord232")
    mqtt_publish_touchpad = not args.mqtt_no_touchpad
    if "mqtt" in config and config.has_option("mqtt", "publish_touchpad"):
        mqtt_publish_touchpad = mqtt_publish_touchpad and config.getboolean(
            "mqtt", "publish_touchpad"
        )
    mqtt_tls = args.mqtt_tls
    if (
        not mqtt_tls
        and "mqtt" in config
        and config.has_option("mqtt", "tls")
    ):
        mqtt_tls = config.getboolean("mqtt", "tls")

    LOG = logging.getLogger()
    LOG.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT)
    istty = os.isatty(0)

    if args.debug and not istty:
        debug_handler = logging.handlers.RotatingFileHandler(
            "debug.log", maxBytes=1024 * 1024 * 10, backupCount=3
        )
        debug_handler.setFormatter(formatter)
        debug_handler.setLevel(logging.DEBUG)
        LOG.addHandler(debug_handler)

    if istty:
        verbose_handler = logging.StreamHandler()
        verbose_handler.setFormatter(formatter)
        verbose_handler.setLevel(args.debug and logging.DEBUG or logging.INFO)
        LOG.addHandler(verbose_handler)

    if log_file:
        log_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024 * 1024 * 10, backupCount=3
        )
        log_handler.setFormatter(formatter)
        log_handler.setLevel(logging.DEBUG)
        LOG.addHandler(log_handler)

    LOG.info("Ready")
    logging.getLogger("connectionpool").setLevel(logging.WARNING)

    if not serial:
        parser.error(
            "The --serial argument or a [server] serial entry in the config file is required. Example: --serial /dev/ttyUSB0"
        )

    # Start Flask first in a non-daemon thread so the API is always reachable
    # on port 5007 even if the serial connection fails or takes time.
    flask_thread = threading.Thread(
        target=lambda: api.app.run(debug=False, host=listen, port=port, threaded=True),
        daemon=False,
        name="flask",
    )
    flask_thread.start()
    LOG.info("API server started on %s:%s", listen, port)

    try:
        ctrl = concord.AlarmPanelInterface(serial, 0.25, LOG)
        api.CONTROLLER = ctrl
        if mqtt_host:
            _setup_mqtt(
                ctrl,
                host=mqtt_host,
                port=mqtt_port,
                username=mqtt_username,
                password=mqtt_password,
                topic_prefix=str(mqtt_topic_prefix),
                client_id=str(mqtt_client_id),
                publish_touchpad=mqtt_publish_touchpad,
                tls=mqtt_tls,
                logger=LOG,
            )
        t = threading.Thread(target=ctrl.message_loop, daemon=True, name="serial-loop")
        t.start()
        t.join()
    except Exception:
        LOG.exception(
            "Serial connection failed; API remains available but panel control is offline"
        )
        flask_thread.join()

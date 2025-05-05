import argparse
import logging
import logging.handlers
import os
import threading
import configparser

from concord232 import api
from concord232 import concord

LOG_FORMAT = '%(asctime)-15s %(module)s %(levelname)s %(message)s'


def main():
    parser = argparse.ArgumentParser(
        description="GE Concord 4 RS232 Serial Interface Server. Provides a Flask API for interacting with the alarm panel.",
        epilog="""
Example usage:
  concord232_server --serial /dev/ttyUSB0 --config myconfig.ini --debug

For more information, see: https://github.com/JasonCarter80/concord232
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--config', default='config.ini',
                        metavar='FILE',
                        help='Path to config file (default: config.ini)')
    parser.add_argument('--debug', default=False, action='store_true',
                        help='Enable debug logging output')
    parser.add_argument('--log', default=None,
                        metavar='FILE',
                        help='Path to log file (default: none; logs to stdout if not set)')
    parser.add_argument('--serial', default=None,
                        metavar='PORT',
                        help='Serial port to open for stream (e.g., /dev/ttyUSB0 or COM3) [REQUIRED]')
    parser.add_argument('--listen', default=None,
                        metavar='ADDR',
                        help='Listen address for the API server (default: 0.0.0.0, all interfaces)')
    parser.add_argument('--port', default=None, type=int,
                        help='Listen port for the API server (default: 5007)')
    args = parser.parse_args()

    # Load config file
    config = configparser.ConfigParser()
    config.read(args.config)
    cfg = config['server'] if 'server' in config else {}

    # Use config values if CLI args are not set
    serial = args.serial or cfg.get('serial')
    listen = args.listen or cfg.get('listen', '0.0.0.0')
    port = args.port or int(cfg.get('port', 5007))
    log_file = args.log or cfg.get('log')

    LOG = logging.getLogger()
    LOG.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT)
    istty = os.isatty(0)

    if args.debug and not istty:
        debug_handler = logging.handlers.RotatingFileHandler(
            'debug.log',
            maxBytes=1024*1024*10,
            backupCount=3)
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
            log_file,
            maxBytes=1024*1024*10,
            backupCount=3)
        log_handler.setFormatter(formatter)
        log_handler.setLevel(logging.DEBUG)
        LOG.addHandler(log_handler)

    LOG.info('Ready')
    logging.getLogger('connectionpool').setLevel(logging.WARNING)

    if not serial:
        parser.error('The --serial argument or a [server] serial entry in the config file is required. Example: --serial /dev/ttyUSB0')

    ctrl = concord.AlarmPanelInterface(serial, 0.25, LOG)
    api.CONTROLLER = ctrl

    t = threading.Thread(target=ctrl.message_loop)
    t.daemon = True
    t.start()
    
    api.app.run(debug=False, host=listen, port=port, threaded=True)

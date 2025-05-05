"""
Flask API for the concord232 server. Provides endpoints for panel, zones, partitions, commands, version, equipment, and all_data.
"""

import flask
import json
import logging
import time

LOG = logging.getLogger("api")
CONTROLLER = None
app = flask.Flask("concord232")
LOG.info("API Code Loaded")


def show_zone(zone):
    """
    Convert a zone dictionary to a JSON-serializable dict for API response.
    Args:
        zone (dict): Zone data.
    Returns:
        dict: JSON-serializable zone info.
    """
    return {
        "partition": zone["partition_number"],
        "area": zone["area_number"],
        "group": zone["group_number"],
        "number": zone["zone_number"],
        "name": zone["zone_text"],
        "state": zone["zone_state"],
        "type": zone["zone_type"],
        #'bypassed': zone.bypassed,
        #'condition_flags': zone.condition_flags,
        #'type_flags': zone.type_flags,
    }


def show_partition(partition):
    """
    Convert a partition dictionary to a JSON-serializable dict for API response.
    Args:
        partition (dict): Partition data.
    Returns:
        dict: JSON-serializable partition info.
    """
    return {
        "number": partition["partition_number"],
        "area": partition["area_number"],
        "arming_level": partition["arming_level"],
        "arming_level_code": partition["arming_level_code"],
        "partition_text": partition["partition_text"],
        "zones": sum(
            z["partition_number"] == partition["partition_number"]
            for z in CONTROLLER.zones.values()
        ),
    }


@app.route("/panel")
def index_panel():
    """
    API endpoint to get the panel state.
    Returns:
        flask.Response: JSON response with panel state.
    """
    try:
        result = json.dumps({"panel": CONTROLLER.panel})
        return flask.Response(result, mimetype="application/json")
    except Exception:
        LOG.exception("Failed to index zones")


@app.route("/zones")
def index_zones():
    """
    API endpoint to get all zones.
    Returns:
        flask.Response: JSON response with all zones.
    """
    try:
        if not bool(CONTROLLER.zones):
            CONTROLLER.request_zones()

        while not bool(CONTROLLER.zones):
            time.sleep(0.25)

        result = json.dumps(
            {"zones": [show_zone(zone) for zone in CONTROLLER.zones.values()]}
        )
        return flask.Response(result, mimetype="application/json")
    except Exception:
        LOG.exception("Failed to index zones")


@app.route("/partitions")
def index_partitions():
    """
    API endpoint to get all partitions.
    Returns:
        flask.Response: JSON response with all partitions.
    """
    try:
        if not bool(CONTROLLER.partitions):
            CONTROLLER.request_partitions()

        while not bool(CONTROLLER.partitions):
            time.sleep(0.25)

        result = json.dumps(
            {
                "partitions": [
                    show_partition(partition)
                    for partition in CONTROLLER.partitions.values()
                ]
            }
        )
        return flask.Response(result, mimetype="application/json")
    except Exception:
        LOG.exception("Failed to index partitions")


@app.route("/command")
def command():
    """
    API endpoint to send commands (arm, disarm, keys) to the panel.
    Returns:
        flask.Response: Empty response.
    """
    args = flask.request.args
    if args.get("cmd") == "arm":
        option = args.get("option")
        if args.get("level") == "stay":
            CONTROLLER.arm_stay(option)
        elif args.get("level") == "away":
            CONTROLLER.arm_away(option)
    elif args.get("cmd") == "disarm":
        CONTROLLER.disarm(args.get("master_pin"))
    elif args.get("cmd") == "keys":
        partition = int(args.get("partition", 1))
        CONTROLLER.send_keys(args.get("keys"), args.get("group"), partition=partition)
    return flask.Response()


@app.route("/version")
def get_version():
    """
    API endpoint to get the API version.
    Returns:
        flask.Response: JSON response with version info.
    """
    return flask.Response(json.dumps({"version": "1.1"}), mimetype="application/json")


@app.route("/equipment")
def get_equipment():
    """
    API endpoint to request all equipment data from the panel.
    Returns:
        flask.Response: Empty response.
    """
    CONTROLLER.request_all_equipment()
    return flask.Response()


@app.route("/all_data")
def get_all_data():
    """
    API endpoint to request a dynamic data refresh from the panel.
    Returns:
        flask.Response: Empty response.
    """
    CONTROLLER.request_dynamic_data_refresh()
    return flask.Response()

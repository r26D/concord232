"""
Flask API for the concord232 server. Provides endpoints for panel, zones, partitions, commands, version, equipment, and all_data.
"""

import json
import logging
import time
from typing import Any, Optional

import flask
from flask import Response

from concord232.concord import AlarmPanelInterface

LOG = logging.getLogger("api")
CONTROLLER: Optional[AlarmPanelInterface] = None
app = flask.Flask("concord232")
LOG.info("API Code Loaded")


def show_zone(zone: dict[str, Any]) -> dict[str, Any]:
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


def show_partition(partition: dict[str, Any]) -> dict[str, Any]:
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
        "zones": (
            sum(
                z["partition_number"] == partition["partition_number"]
                for z in CONTROLLER.zones.values()
            )
            if CONTROLLER is not None and hasattr(CONTROLLER, "zones")
            else 0
        ),
    }


@app.route("/panel")
def index_panel() -> Any:
    """
    API endpoint to get the panel state.
    Returns:
        flask.Response: JSON response with panel state.
    """
    if CONTROLLER is None:
        return Response("Controller not initialized", status=503)
    try:
        result = json.dumps({"panel": CONTROLLER.panel})
        return Response(result, mimetype="application/json")
    except Exception:
        LOG.exception("Failed to index zones")


@app.route("/zones")
def index_zones() -> Any:
    """
    API endpoint to get all zones.
    Returns:
        flask.Response: JSON response with all zones.
    """
    if CONTROLLER is None:
        return Response("Controller not initialized", status=503)
    try:
        if not bool(CONTROLLER.zones):
            CONTROLLER.request_zones()

        while not bool(CONTROLLER.zones):
            time.sleep(0.25)

        result = json.dumps(
            {"zones": [show_zone(zone) for zone in CONTROLLER.zones.values()]}
        )
        return Response(result, mimetype="application/json")
    except Exception:
        LOG.exception("Failed to index zones")


@app.route("/partitions")
def index_partitions() -> Any:
    """
    API endpoint to get all partitions.
    Returns:
        flask.Response: JSON response with all partitions.
    """
    if CONTROLLER is None:
        return Response("Controller not initialized", status=503)
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
        return Response(result, mimetype="application/json")
    except Exception:
        LOG.exception("Failed to index partitions")


@app.route("/command")
def command() -> Any:
    """
    API endpoint to send commands (arm, disarm, keys) to the panel.
    Returns:
        flask.Response: Empty response.
    """
    if CONTROLLER is None:
        return Response("Controller not initialized", status=503)
    args = flask.request.args
    if args.get("cmd") == "arm":
        option = args.get("option")
        if args.get("level") == "stay":
            CONTROLLER.arm_stay(option)
        elif args.get("level") == "away":
            CONTROLLER.arm_away(option)
    elif args.get("cmd") == "disarm":
        master_pin = args.get("master_pin")
        if master_pin is not None:
            CONTROLLER.disarm(str(master_pin))
        else:
            return Response("Missing master_pin", status=400)
    elif args.get("cmd") == "keys":
        keys = args.get("keys")
        group = args.get("group")
        partition = int(args.get("partition", 1))
        keys_list = list(keys) if keys is not None else []
        CONTROLLER.send_keys(
            keys_list, bool(group) if group is not None else False, partition=partition
        )
    return Response()


@app.route("/version")
def get_version() -> Any:
    """
    API endpoint to get the API version.
    Returns:
        flask.Response: JSON response with version info.
    """
    return flask.Response(json.dumps({"version": "1.1"}), mimetype="application/json")


@app.route("/equipment")
def get_equipment() -> Any:
    """
    API endpoint to request all equipment data from the panel.
    Returns:
        flask.Response: Empty response.
    """
    if CONTROLLER is None:
        return Response("Controller not initialized", status=503)
    CONTROLLER.request_all_equipment()
    return Response()


@app.route("/all_data")
def get_all_data() -> Any:
    """
    API endpoint to request a dynamic data refresh from the panel.
    Returns:
        flask.Response: Empty response.
    """
    if CONTROLLER is None:
        return Response("Controller not initialized", status=503)
    CONTROLLER.request_dynamic_data_refresh()
    return Response()
